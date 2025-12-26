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

def set_dropdown(locator, project_root):
  moverPara(147,297)
  click()
  press('down', 4)
  enter()

def processando():
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


def main():
    # Ativa e maximiza a janela SCENE
    activate_and_maximize_scene_window()

    status = StatusWindow()  # <<< ADICIONAR
    status.update("🚀 Iniciando automação...")  # <<< ADICIONAR

    locator = ButtonLocator(llm_model="gemma3:12b")

    # Pega o diretório do script (zCode/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Sobe um nível para ANP/ (raiz do projeto)
    project_root = os.path.dirname(script_dir)



 







    #####################################
    ### Aqui começa o MAIN de verdade ###
    #####################################
    try:
        #Essa variavel será usada so no final do loop
        status.update("🔍 Listando clusters da página inicial...")  # <<< ADICIONAR
        clusters_main_page = locator.list_clusters()
        print(clusters_main_page)

        status.update("📍 Localizando botão 'Registro Automático'...")  # <<< ADICIONAR
        template_path = os.path.join(project_root, "buttons", "registro_automatico.png")
        use_template = template_path if os.path.exists(template_path) else None

        result = locator.locate_tm(
            button_name="",
            use_template=use_template,
            validate_llm=False
        )

        #notify(f"{result['found']},{result['x']},{result['y']}", title="ANP", duration=1)
        moverPara(result['x'], result['y'])
        click()
        time.sleep(3)
    except:
        status.update("❌ Erro ao localizar botão inicial")  # <<< ADICIONAR
        notify("Ocorreu um erro inesperado", title="ANP", duration=1)

    # Escaneia os clusters_reg_auto
    try:
        status.update("🔎 Identificando clusters... Aguarde")  # <<< ADICIONAR
        notify("Iniciando identificação de clusters... Isso pode levar um tempo", title="ANP", duration=1)
        clusters_reg_auto = locator.list_items_below("Scans")
        #notify("Escaneado com sucesso!", title="ANP", duration=1)
        print(clusters_reg_auto)

        # Clica nos clusters encontrados
        for nome, coords in clusters_reg_auto.items():
            status.update(f"🖱️ Processando {nome}...")  # <<< ADICIONAR
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
                    set_dropdown(locator, project_root)

                    # ============ AJUSTE DOS INPUTS ==============
                    status.update(f"🎚️ Ajustando parâmetros...")  # <<< ADICIONAR
                    adjust_sliders_to_target([0.070, 0.2, 0.044])

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
                        if processando():
                            print(f"⏳ Aguardando fim do processamento...")
                            status.update(f"⏳ Aguardando fim do processamento...")
                            time.sleep(5)
                        else:
                            break
                    #Aqui podemos ter algumas paginas diferentes dependendo do resultado
                    #Precisamos fazer tratamento para todas as ocasiões
                    



                    #Pagina 1, clássica = inicial
                    #Click no botao de resultado
                    status.update(f"✅ Finalizando {nome}...")  # <<< ADICIONAR
                    time.sleep(2)
                    print(clusters_main_page)
                    y = clusters_main_page[nome]['y']
                    moverPara(1136, y)
                    click()
                    time.sleep(1)

                ###########
                ########### Após Entrar no relatório ###############
                ###########
                    locator.read_report()


                    ##SISTEMA DE ARMAZENAMENTO DAS VARIAVEIS
                    ##CODE

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
                    #notify(f"{result['found']},{result['x']},{result['y']}", title="ANP", duration=1)
                    moverPara(result['x'], result['y'])
                    click()

                    


                    
                    
                    
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
    
    status.update("🏁 Automação concluída!")  # <<< ADICIONAR

if __name__ == "__main__":
    main()