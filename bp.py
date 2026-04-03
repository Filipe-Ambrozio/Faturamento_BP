import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title='Faturamento e Despesas', layout='wide')

APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxtm8qKPHX2ayfmPVL9v814Y86OHFSihV8FmHewcW31QUZ7Tesm5WSeVI31bTAp_4Hw_w/exec'

# Listas de lojas e tipos de despesas
LOJAS = [
    "Boa Opção São Lourenço",
    "Boa Opção Timbaúba",
    "Boa Opção Peixinho",
    "BM SL",
    "BM Porto",
    "BM Santa Rita",
    "BM Timbaúba",
    "BM Abreu",
    "BM Surubim",
    "BM Natal",
    "BM Campina"
]

TIPOS_DESPESA = [
    "Doação",
    "Lanche",
    "MT-Escritório",
    "MT-Limpeza",
    "MT-Loja",
    "MT-Manutenção",
    "Ornamentação",
    "Pagamento",
    "Publicidade",
    "Refeição",
    "Segurança",
    "Serviços",
    "Veículo"
]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

if 'message' not in st.session_state:
    st.session_state.message = ''

if 'despesas_lista' not in st.session_state:
    st.session_state.despesas_lista = []


def login(username, password):
    if username == 'admin' and password == '20253':
        st.session_state.logged_in = True
        st.session_state.user = username
        st.session_state.message = ''
    else:
        st.session_state.message = 'Usuário ou senha inválido.'


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None


def get_data():
    try:
        r = requests.get(APPS_SCRIPT_URL, timeout=20)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=300)
def get_data_cached():
    """Cacheia dados por 5 minutos (300 segundos)"""
    return get_data()


def post_data(payload):
    """Envia dados para o Web App com retry automático (máx 2 tentativas)"""
    headers = {'Content-Type': 'application/json'}
    max_tentativas = 2
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            r = requests.post(APPS_SCRIPT_URL, json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            return r.text, None
        except requests.exceptions.Timeout:
            if tentativa < max_tentativas:
                st.warning(f'⏳ Timeout na tentativa {tentativa}... tentando novamente...')
                continue
            else:
                return None, f'Timeout após {max_tentativas} tentativas. Tente novamente em alguns segundos.'
        except Exception as e:
            return None, str(e)
    
    return None, 'Erro desconhecido ao salvar.'


@st.cache_data(ttl=300)
def processar_dataframes(dados_json):
    """Cacheia o processamento dos DataFrames por 5 minutos"""
    df_fat = None
    df_desp = None

    if 'faturamento' in dados_json and dados_json['faturamento']:
        df_fat = pd.DataFrame(dados_json['faturamento'])
        if 'data' in df_fat.columns:
            df_fat['data'] = pd.to_datetime(df_fat['data'], dayfirst=True, errors='coerce')
            df_fat['ano'] = df_fat['data'].dt.year
            df_fat['mes'] = df_fat['data'].dt.month

    if 'despesas' in dados_json and dados_json['despesas']:
        df_desp = pd.DataFrame(dados_json['despesas'])
        if 'data' in df_desp.columns:
            df_desp['data'] = pd.to_datetime(df_desp['data'], dayfirst=True, errors='coerce')
            df_desp['ano'] = df_desp['data'].dt.year
            df_desp['mes'] = df_desp['data'].dt.month

    return df_fat, df_desp


if not st.session_state.logged_in:
    st.title('Login - Faturamento e Despesas')
    with st.form(key='login_form'):
        # username = st.text_input('Usuário', value='admin')
        # password = st.text_input('Senha', type='password', value='1234')
        username = st.text_input('Usuário', value='')
        password = st.text_input('Senha', type='password', value='')
        enviar = st.form_submit_button('Entrar')

        if enviar:
            login(username, password)

    if st.session_state.message:
        st.error(st.session_state.message)

    st.markdown('**TheeF** do Brazil `versão`, Abril2026 `V.1001.2`.')
    st.stop()


st.sidebar.write(f'Olá, {st.session_state.user}!')
if st.sidebar.button('Sair'):
    logout()
    st.rerun()

st.title('Controle de Faturamento e Despesas')

tabs = st.tabs(['Registrar', 'Dados atuais da planilha'])

with tabs[0]:
    st.subheader('Registrar Faturamento e Despesas')
    
    # Campos compartilhados no topo (fora das abas)
    st.markdown('### 📋 Dados do Registro')
    col_top = st.columns(3)
    with col_top[0]:
        data_registro = st.date_input('Data', value=datetime.now().date(), key='data_registro')
    with col_top[1]:
        loja_registro = st.selectbox('Loja', LOJAS, key='loja_registro')
    with col_top[2]:
        nome_registro = st.text_input('Nome do cliente', key='nome_registro')
    
    st.markdown('---')
    
    # Abas internas
    tab_reg = st.tabs(['Faturamento', 'Adicionar Despesas'])
    
    with tab_reg[0]:
        st.markdown('### 💰 Registrar Faturamento')
        
        col1, col2 = st.columns(2)
        with col1:
            dinheiro = st.number_input('Dinheiro', min_value=0.0, format='%.2f', key='dinheiro_fat')
            infinity = st.number_input('Infinity', min_value=0.0, format='%.2f', key='infinity_fat')
            stone = st.number_input('Stone', min_value=0.0, format='%.2f', key='stone_fat')
        with col2:
            vale = st.number_input('Vale', min_value=0.0, format='%.2f', key='vale_fat')
            pix = st.number_input('Pix', min_value=0.0, format='%.2f', key='pix_fat')
        
        # Soma automática de faturamento
        soma_faturamento = dinheiro + infinity + stone + vale + pix
        st.success(f'💵 **Soma de faturamento:** R$ {soma_faturamento:.2f}')
        
        st.markdown('---')
        st.markdown('### 📦 Despesas Adicionadas')
        
        # Exibir lista de despesas adicionadas
        despesa_display = []
        for idx, item in enumerate(st.session_state.despesas_lista, 1):
            despesa_display.append({
                '#': idx,
                'Tipo': item['tipo'],
                'Valor': f"R$ {item['valor']}",
                'Descrição': item['descricao']
            })

        if despesa_display:
            st.dataframe(despesa_display, use_container_width=True, hide_index=True)
            soma_despesa = sum(float(x['valor']) for x in st.session_state.despesas_lista)
            st.info(f'💰 **Total de despesas:** R$ {soma_despesa:.2f}')
        else:
            soma_despesa = 0.0
            st.info('📝 Nenhuma despesa cadastrada ainda. O faturamento será salvo sozinho.')

        soma_total = soma_faturamento + soma_despesa
        st.warning(f'📊 **SOMA TOTAL:** R$ {soma_total:.2f}')

        st.markdown('---')
        st.markdown('### 💾 Salvar Tudo')

        col_btn_final = st.columns(2)
        with col_btn_final[0]:
            if st.button('✅ Salvar Faturamento + Despesas', use_container_width=True, type='primary'):
                # Validação rápida
                if not loja_registro or not nome_registro:
                    st.error('❌ Preencha Loja e Nome do cliente obrigatoriamente!')
                else:
                    with st.spinner('💾 Salvando... por favor aguarde (pode levar 30s)...'):
                        payload = {
                            'data': data_registro.strftime('%Y-%m-%d'),
                            # 'data': data_registro.strftime('%d-%m-%y'),
                            'loja': loja_registro,
                            'nome': nome_registro,
                            'dinheiro': f'{dinheiro:.2f}',
                            'infinity': f'{infinity:.2f}',
                            'stone': f'{stone:.2f}',
                            'vale': f'{vale:.2f}',
                            'pix': f'{pix:.2f}',
                            'total_despesa': f'{soma_despesa:.2f}',
                            'total_final': f'{soma_total:.2f}',
                            'lista_despesas': st.session_state.despesas_lista
                        }
                        text, err = post_data(payload)
                        if err:
                            st.error('❌ Erro ao salvar: ' + err)
                        else:
                            st.success('✅ Faturamento + Despesas salvos com sucesso!')
                            st.session_state.despesas_lista = []
                            st.session_state.clear()
                            st.rerun()

        with col_btn_final[1]:
            if st.button('🗑️ Limpar Despesas', use_container_width=True):
                st.session_state.despesas_lista = []
                st.rerun()

    with tab_reg[1]:
        st.markdown('### ➕ Adicionar Despesas em Lote')
        st.write(f'**Data:** {data_registro.strftime("%y/%m/%d")} | **Loja:** {loja_registro} | **Cliente:** {nome_registro}')
        st.markdown('---')
        
        col_desp_form = st.columns([2, 1, 2])
        with col_desp_form[0]:
            tipo_item = st.selectbox('Tipo de despesa', TIPOS_DESPESA, key='tipo_item_form')
        with col_desp_form[1]:
            valor_item = st.number_input('Valor (R$)', min_value=0.0, format='%.2f', key='valor_item_form')
        with col_desp_form[2]:
            desc_item = st.text_input('Descrição', key='desc_item_form')

        col_btn = st.columns([1, 4])
        with col_btn[0]:
            if st.button('➕ Adicionar', use_container_width=True):
                if valor_item > 0:
                    st.session_state.despesas_lista.append({
                        'valor': f'{valor_item:.2f}',
                        'tipo': tipo_item,
                        'descricao': desc_item
                    })
                    st.success('✅ Despesa adicionada!')
                    st.rerun()
                else:
                    st.warning('⚠️ Valor deve ser maior que zero!')

        # Lista de despesas pendentes
        if st.session_state.despesas_lista:
            st.markdown('---')
            st.markdown('### 📋 Despesas Pendentes')
            
            for idx, item in enumerate(st.session_state.despesas_lista):
                col_item = st.columns([0.5, 2, 1, 2, 0.5])
                with col_item[0]:
                    st.write(f"{idx+1}")
                with col_item[1]:
                    st.write(item['tipo'])
                with col_item[2]:
                    st.write(f"R$ {item['valor']}")
                with col_item[3]:
                    st.write(item['descricao'])
                with col_item[4]:
                    if st.button('🗑️', key=f'del_desp_{idx}', help='Remover'):
                        st.session_state.despesas_lista.pop(idx)
                        st.rerun()
            
            soma_desp = sum(float(x['valor']) for x in st.session_state.despesas_lista)
            st.info(f'💰 **Total adicionado:** R$ {soma_desp:.2f}')
        else:
            st.info('Nenhuma despesa adicionada ainda.')


with tabs[1]:
    st.subheader('Dados atuais da planilha')
    
    # Lazy loading com cache (ttl=300 = 5 minutos)
    with st.spinner('⏳ Carregando dados (cache por 5 min)...'):
        dados, erro = get_data_cached()
    
    if erro:
        st.error('❌ Não foi possível ler dados do Web App: ' + erro)
    else:
        col_refresh = st.columns([1, 5])
        with col_refresh[0]:
            if st.button('🔄 Atualizar dados', key='btn_refresh'):
                st.cache_data.clear()
                st.rerun()
        
        with col_refresh[1]:
            st.caption('(dados em cache por 5 min, clique para atualizar agora)')
        
        # Processar DataFrames com cache
        df_fat, df_desp = processar_dataframes(dados)

        # Filtros predefinidos
        anos_fat = df_fat['ano'].dropna().astype(int).unique().tolist() if df_fat is not None else []
        anos_desp = df_desp['ano'].dropna().astype(int).unique().tolist() if df_desp is not None else []
        anos = sorted(set(anos_fat + anos_desp))

        lojas_fat = df_fat['loja'].dropna().unique().tolist() if (df_fat is not None and 'loja' in df_fat.columns) else []
        lojas_desp = df_desp['loja'].dropna().unique().tolist() if (df_desp is not None and 'loja' in df_desp.columns) else []
        lojas = sorted(set(lojas_fat + lojas_desp))

        ano_selecionado = st.selectbox('Ano', options=['Todos'] + [str(int(a)) for a in anos]) if anos else 'Todos'
        mes_selecionado = st.selectbox('Mês', options=['Todos'] + [f'{m:02d}' for m in range(1, 13)])
        loja_selecionada = st.selectbox('Loja', options=['Todas'] + lojas) if lojas else 'Todas'

        # Aplicar filtros
        def aplicar_filtros(df):
            if df is None:
                return None
            filtered = df.copy()
            if ano_selecionado != 'Todos' and 'ano' in filtered.columns:
                filtered = filtered[filtered['ano'] == int(ano_selecionado)]
            if mes_selecionado != 'Todos' and 'mes' in filtered.columns:
                filtered = filtered[filtered['mes'] == int(mes_selecionado)]
            if loja_selecionada != 'Todas' and 'loja' in filtered.columns:
                filtered = filtered[filtered['loja'] == loja_selecionada]
            return filtered

        df_fat_filtrado = aplicar_filtros(df_fat)
        df_desp_filtrado = aplicar_filtros(df_desp)

        # Exibir abas com dados filtrados
        tab_dados = st.tabs(['Faturamento', 'Despesas'])

        with tab_dados[0]:
            st.markdown('**Faturamento**')
            if df_fat_filtrado is not None and not df_fat_filtrado.empty:
                st.dataframe(df_fat_filtrado, use_container_width=True)

                total_fat = 0.0
                if 'total_final' in df_fat_filtrado.columns:
                    total_fat = pd.to_numeric(df_fat_filtrado['total_final'], errors='coerce').fillna(0).sum()
                st.success(f'💵 **Total de faturamento filtrado:** R$ {total_fat:.2f}')
            else:
                st.info('📭 Nenhum faturamento encontrado para os filtros.')

        with tab_dados[1]:
            st.markdown('**Despesas**')
            if df_desp_filtrado is not None and not df_desp_filtrado.empty:
                st.dataframe(df_desp_filtrado, use_container_width=True)

                # soma valor de despesas
                if 'valor' in df_desp_filtrado.columns:
                    total_desp = pd.to_numeric(df_desp_filtrado['valor'], errors='coerce').fillna(0).sum()
                elif 'despesa' in df_desp_filtrado.columns:
                    total_desp = pd.to_numeric(df_desp_filtrado['despesa'], errors='coerce').fillna(0).sum()
                else:
                    total_desp = 0.0
                st.warning(f'⚠️ **Total de despesas filtrado:** R$ {total_desp:.2f}')
            else:
                st.info('📭 Nenhuma despesa encontrada para os filtros.')

        # Botões de exportação
        st.markdown('---')
        st.markdown('### 💾 Exportar dados')

        if df_fat is not None or df_desp is not None:
            # Exportar XLSX completo
            df_fat_export = df_fat_filtrado.copy() if df_fat_filtrado is not None else None
            df_desp_export = df_desp_filtrado.copy() if df_desp_filtrado is not None else None

            # Remover timezone para compatibilidade com Excel
            for df in [df_fat_export, df_desp_export]:
                if df is not None:
                    for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                        try:
                            df[col] = df[col].dt.tz_localize(None)
                        except Exception:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.tz_localize(None)

            buffer_xlsx = io.BytesIO()
            with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
                if df_fat_export is not None:
                    df_fat_export.to_excel(writer, sheet_name='Faturamento', index=False)
                if df_desp_export is not None:
                    df_desp_export.to_excel(writer, sheet_name='Despesas', index=False)
            buffer_xlsx.seek(0)

            st.download_button(
                label='📥 Baixar XLSX (Faturamento + Despesas)',
                data=buffer_xlsx,
                file_name='planilha_exportada.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            # Exportar CSVs separados
            if df_fat_filtrado is not None:
                csv_fat = df_fat_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label='📥 Baixar Faturamento CSV',
                    data=csv_fat,
                    file_name='faturamento_filtrado.csv',
                    mime='text/csv'
                )

            if df_desp_filtrado is not None:
                csv_desp = df_desp_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label='📥 Baixar Despesas CSV',
                    data=csv_desp,
                    file_name='despesas_filtradas.csv',
                    mime='text/csv'
                )


st.sidebar.markdown('### 📖 Instruções')
st.sidebar.write('✅ Login e senha para entrar.')
st.sidebar.write('✅ Aba Registrar → Faturamento: soma automática em tempo real.')
st.sidebar.write('✅ Aba Registrar → Despesas: adicione múltiplos itens, depois salve tudo.')
st.sidebar.write('✅ Soma de despesas atualiza instantaneamente.')
st.sidebar.write('✅ Aba Dados: lazy loading, carrega dados ao clicar.')
st.sidebar.write('✅ Botão Sair retorna ao login.')


