from button_locator import ButtonLocator
from simple.window_manager import activate_and_maximize_scene_window
import time
import pyautogui
import os
from simple.moves import click, moverPara, enter, press
from simple.notifications import notify
import ollama
from set_new_values_slidebar import adjust_sliders_to_target
from status_window import StatusWindow  # <<< ADICIONAR
from context import context
from target_optimizer import TargetOptimizer
from database_manager import DatabaseManager



class Main:
    def __init__(self):
        self.clusters_main_page = None

    def set_dropdown(self):
        moverPara(147,297)
        click()
        press('down', 4)
        enter()

    def processando(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        template_path = os.path.join(project_root, "buttons", "registro_em_andamento.png")


        locator = ButtonLocator()
        screenshot = locator.capture_screen()

        # Salva screenshot pra você ver o que ele tá capturando
        screenshot.save("./salvos/debug_screenshot.png")
        result = locator.find_with_template(screenshot, template_path)
        if result['found']:
            return True
        else:
            return False
        

    def verificar_falha_registro(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        template_path = os.path.join(project_root, "buttons", "falha_no_registro.png")


        locator = ButtonLocator()
        screenshot = locator.capture_screen()

        # Salva screenshot pra você ver o que ele tá capturando
        screenshot.save("./salvos/debug_screenshot.png")
        result = locator.find_with_template(screenshot, template_path)
        if result['found']:
            return True
        else:
            return False



    def registroAutomatico(self):
        status = StatusWindow()  # <<< ADICIONAR
        status.update("🚀 Iniciando automação...")  # <<< ADICIONAR

        locator = ButtonLocator(llm_model="gemma3:12b")

        # Pega o diretório do script (zCode/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Sobe um nível para ANP/ (raiz do projeto)
        project_root = os.path.dirname(script_dir)

        try:
            #Essa variavel será usada so no final do loop
            status.update("🔍 Listando clusters da página inicial...")  # <<< ADICIONAR
            self.clusters_main_page = locator.list_clusters()
            print(self.clusters_main_page)

            status.update("📍 Localizando botão 'Registro Automático'...")  # <<< ADICIONAR
            template_path = os.path.join(project_root, "buttons", "registro_automatico.png")
            use_template = template_path if os.path.exists(template_path) else None

            result = locator.locate_tm(
                button_name="",
                use_template=use_template,
                validate_llm=False
            )
            moverPara(result['x'], result['y'])
            click()
            time.sleep(3)
        except:
            status.update("❌ Erro ao localizar botão inicial")  # <<< ADICIONAR
            notify("Ocorreu um erro inesperado", title="ANP", duration=1)





    def main(self):
        # Ativa e maximiza a janela SCENE
        activate_and_maximize_scene_window()
        time.sleep(1)
        context.set_project_from_window() # << SETA O NOME DO PROJETO
        context.set_static_inputs(.5, 10, 30)
        context.set_minimum_dinamic_inputs(.5, .10)
        
        status = StatusWindow()  # <<< ADICIONAR
        status.update("🚀 Iniciando automação...")  # <<< ADICIONAR

        locator = ButtonLocator(llm_model="gemma3:12b")

        target = TargetOptimizer()

        db = DatabaseManager()



        # Pega o diretório do script (zCode/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Sobe um nível para ANP/ (raiz do projeto)
        project_root = os.path.dirname(script_dir)



    







        #####################################
        ### Aqui começa o MAIN de verdade ###
        #####################################
        self.registroAutomatico()


        # Escaneia os clusters_reg_auto
        try:
            status.update("🔎 Identificando clusters... Aguarde")  # <<< ADICIONAR
            notify("Iniciando identificação de clusters... Isso pode levar um tempo", title="ANP", duration=1)
            clusters_reg_auto = locator.list_items_below("Scans")

            # Clica nos clusters encontrados
            for nome, coords in clusters_reg_auto.items():
                while True:
                    status.update(f"🖱️ Processando {nome}...")  # <<< ADICIONAR
                    context.set_cluster(nome)

                    moverPara(coords['x'], coords['y'])
                    click()

                    # Clica em "Selecionar método"            
                    try:
                        status.update(f"⚙️ Configurando método para {nome}...")  # <<< ADICIONAR
                        template_path = os.path.join(project_root, "buttons", "selecionar_metodo.png")
                        use_template = template_path if os.path.exists(template_path) else None

                        success = locator.locate_tm(
                            button_name="Selecionar método",
                            use_template=use_template,
                            validate_llm=True
                        )

                        if success:
                            found_coords = locator.last_found_coords
                            moverPara(found_coords['x'], found_coords['y'])
                            click()

                            # ============ VERIFICAR E SELECIONAR DROPDOWN ============
                            time.sleep(1)
                            self.set_dropdown()

                            # ============ AJUSTE DOS INPUTS ==============
                            status.update(f"🧮 Calculando novos inputs...") 
                            targets = target.get_new_targets()
                            status.update(f"🎚️ Ajustando parâmetros...")  
                            adjust_sliders_to_target(targets)

                            #============= CLICA PARA INICIAR O CICLO ==========
                            try:
                                status.update(f"▶️ Iniciando registro de {nome}...")  # <<< ADICIONAR
                                template_path = os.path.join(project_root, "buttons", "registrar_e_verificar.png")
                                use_template = template_path if os.path.exists(template_path) else None

                                result = locator.locate_tm(
                                    button_name="",
                                    use_template=use_template,
                                    validate_llm=False
                                )
                                moverPara(result['x'], result['y'])
                                click()

                            except:
                                input("Error...")
                            ## ------- Aqui precisa de um sistema que espera o final do carregamento ---
                            while True:
                                if self.processando():
                                    print(f"⏳ Aguardando fim do processamento...")
                                    status.update(f"⏳ Aguardando fim do processamento...")
                                    time.sleep(5)
                                else:
                                    break
                            #Aqui podemos ter algumas paginas diferentes dependendo do resultado
                            #Precisamos fazer tratamento para todas as ocasiões
                            

                            #Pagina 1, falha no reigstro
                            if self.verificar_falha_registro():
                                status.update(f"⚠️ Parâmetros insuficientes. Incluindo na análise e tentando novamente...")
                                
                                analysis_id, numero_analise = db.insert_analysis(
                                nome_projeto=context.nome_projeto,
                                cluster=context.cluster,
                                input1=targets[0], # O valor que você usou
                                input2=context.static_inputs['x2'],
                                input3=targets[2],
                                input4=context.static_inputs.get('x4'), # Opcional
                                input5=context.static_inputs.get('x5'), # Opcional
                                output1=float(0), # EPM
                                output2=float(0), # MEP
                                output3=float(0) # SM
                            )
                                
                                time.sleep(5)
                                moverPara(877,453) #Perigoso, mudar depois
                                click()
                            else:
                                #Pagina 2, clássica = inicial
                                #Click no botao de resultado
                                status.update(f"✅ Finalizando {nome}...")  # <<< ADICIONAR
                                time.sleep(2)
                                print(self.clusters_main_page)
                                y = self.clusters_main_page[nome]['y']
                                moverPara(1136, y)
                                click()
                                time.sleep(1)

                            ###########
                            ########### Após Entrar no relatório ###############
                            ###########
                                report_values = locator.read_report()
                                
                                ##SISTEMA DE ARMAZENAMENTO DAS VARIAVEIS
                                ##PRÉ PRÉ TRATAMENTO
                                outputs_limpos = [x.replace(' ', '').replace('%', '').replace('mm', '') for x in report_values]

                                analysis_id, numero_analise = db.insert_analysis(
                                    nome_projeto=context.nome_projeto,
                                    cluster=context.cluster,
                                    input1=targets[0], # O valor que você usou
                                    input2=context.static_inputs['x2'],
                                    input3=targets[2],
                                    input4=context.static_inputs.get('x4'), # Opcional
                                    input5=context.static_inputs.get('x5'), # Opcional
                                    output1=float(outputs_limpos[0]), # EPM
                                    output2=float(outputs_limpos[1]), # MEP
                                    output3=float(outputs_limpos[2]) # SM
                                )
                                
                                

                                ##SISTEMA DE OTIMIZAÇÃO PARA CALCULO DE NOVOS TARGETS
                                ##CODE

                                ##FECHAR RELATÓRIO E REINICIAR LOOP
                                status.update("📍 Fechando relatório...")  # <<< ADICIONAR
                                template_path = os.path.join(project_root, "buttons", "fechar_relatorio.png")
                                use_template = template_path if os.path.exists(template_path) else None

                                result = locator.locate_tm(
                                    button_name="",
                                    use_template=use_template,
                                    validate_llm=False
                                )
                                
                                moverPara(result['x'], result['y'])
                                click()
                                time.sleep(1)
                            self.registroAutomatico()
                            
                            
                            ##############################
                            # Análise Critério de parada #
                            ##############################

                            if context.criterio <= float(outputs_limpos[2]):
                                break
                            else:
                                pass

                            
                            
                            
                        else:
                            input("End")
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        found_coords = locator.last_ocr_coords

                    if found_coords:
                        pyautogui.moveTo(found_coords['x'], found_coords['y'], duration=0.5)
        except:
            status.update("❌ Erro na identificação de clusters")  # <<< ADICIONAR
            input("Falha no sistema de identificação de clusters, aperte ENTER para continuar...")
        
        status.update(f"✅ Clusters Finalizados com sucesso!")  # <<< ADICIONAR
        input()

        

if __name__ == "__main__":
    app = Main()
    app.main()