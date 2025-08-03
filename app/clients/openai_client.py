# app/clients/openai_client.py
import os, time, json, logging, re
from openai import OpenAI
from app.functions import AVAILABLE_FUNCTIONS

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ASSISTANT_ID = os.environ.get("OPENAI_ASSISTANT_ID")
user_thread_map = {} # Em produção, mova para um DB (Redis)

def _sanitize(text: str) -> str:
    if not text: return ""
    text = re.sub(r'【.*?】', '', text)
    return re.sub(r'\s{2,}', ' ', text).strip()

def _get_or_create_thread(session_id: str):
    tid = user_thread_map.get(session_id)
    if tid: return tid
    try:
        thread = client.beta.threads.create(metadata={"session_id": session_id})
        user_thread_map[session_id] = thread.id
        logger.info(f"[THREAD] Criada thread id={thread.id} para sessão={session_id}")
        return thread.id
    except Exception as e:
        logger.error(f"Erro ao criar thread: {e}", exc_info=True)
        return None

def orchestrate_assistant_response(session_id: str, user_input: str, from_user: str, to_bot: str):
    if not ASSISTANT_ID:
        logger.error("[ORQUESTRADOR] OPENAI_ASSISTANT_ID ausente.")
        return

    try:
        logger.info(f"[ORQUESTRADOR INICIADO] Sessão={session_id}, Input={user_input[:50]}...")
        
        thread_id = _get_or_create_thread(session_id)
        if not thread_id:
            from app.functions import send_whatsapp_message
            send_whatsapp_message(to=from_user, body="Desculpe, tive um problema técnico. Pode tentar novamente?")
            return

        # Adiciona mensagem do usuário
        logger.info(f"[MESSAGE ADD] Adicionando mensagem do usuário na thread {thread_id}")
        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

        # Cria execução
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)
        logger.info(f"[RUN CREATE] ID={run.id} para sessão={session_id}")

        start = time.time()
        while time.time() - start < 90: # Timeout de 90s
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            logger.info(f"[RUN STATUS] ID={run.id}, Status={run.status}")

            if run.status == "requires_action":
                tool_outputs = []
                calls = run.required_action.submit_tool_outputs.tool_calls if run.required_action and run.required_action.submit_tool_outputs else []
                logger.info(f"[RUN ACTION] Assistente solicitou {len(calls)} função(ões)")
                
                for tool_call in calls:
                    func_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Passa o 'to' (número do usuário) para as funções de envio
                    if 'send_whatsapp' in func_name:
                        arguments['to'] = from_user
                    
                    # Passa o 'session_id' para as funções que precisam dele
                    if func_name in ['rag_query']:
                        arguments['session_id'] = session_id
                    
                    function_to_call = AVAILABLE_FUNCTIONS.get(func_name)
                    if function_to_call:
                        logger.info(f"[FUNCTION CALL] Executando '{func_name}' com args: {arguments}")
                        try:
                            output = function_to_call(**arguments)
                            tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})
                            logger.info(f"[FUNCTION SUCCESS] '{func_name}' executada com sucesso")
                        except Exception as e:
                            error_msg = f"Erro na função {func_name}: {e}"
                            logger.error(f"[FUNCTION ERROR] {error_msg}", exc_info=True)
                            tool_outputs.append({"tool_call_id": tool_call.id, "output": error_msg})
                    else:
                        error_msg = f"Função '{func_name}' não encontrada"
                        logger.error(f"[FUNCTION NOT FOUND] {error_msg}")
                        tool_outputs.append({"tool_call_id": tool_call.id, "output": error_msg})
                
                client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)

            elif run.status == "completed":
                logger.info(f"[RUN COMPLETED] ID={run.id}. Orquestração finalizada.")
                return  # O trabalho acabou, as functions já enviaram as mensagens

            elif run.status in ("failed","cancelled","expired"):
                logger.error(f"[RUN FAILED] ID={run.id}, Status={run.status}, Erro: {run.last_error}")
                from app.functions import send_whatsapp_message
                send_whatsapp_message(to=from_user, body="Desculpe, minha linha de raciocínio foi interrompida. Pode tentar de novo?")
                return
            
            time.sleep(1.5) # Aumenta um pouco a pausa entre as verificações

        logger.error(f"[RUN TIMEOUT] A execução do Run {run.id} excedeu 90 segundos.")
        from app.functions import send_whatsapp_message
        send_whatsapp_message(to=from_user, body="Desculpe, demorei muito para processar. Pode tentar uma pergunta mais simples?")

    except Exception as e:
        logger.error(f"[ORQUESTRADOR CRASH] Erro inesperado: {e}", exc_info=True)
        from app.functions import send_whatsapp_message
        send_whatsapp_message(to=from_user, body="Erro interno. Tente novamente.")
        _send_fallback_message(from_user, "Ops, tive um problema interno. Pode tentar novamente?")