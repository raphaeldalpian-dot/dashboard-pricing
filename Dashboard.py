import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import glob

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Pricing Analytics UI", layout="wide", initial_sidebar_state="collapsed")

# 2. INJEÇÃO DE CSS AVANÇADO (Tema Escuro, Vermelho, Degradês e Animações)
st.markdown("""
<style>
    /* Fundo principal super escuro (Deep Space Black) */
    .stApp { background-color: #0a0b10; }
    
    /* Configuração global de texto */
    h1, h2, h3, p, span, div { color: #e2e8f0; font-family: 'Inter', 'Segoe UI', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Seção de Filtros Superior */
    .filter-section {
        background: linear-gradient(90deg, #12141d 0%, #0a0b10 100%);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 25px;
        border: 1px solid #1f2333;
        border-left: 4px solid #ff2a2a;
    }

    /* CARDS DE KPI (Estilo Dashboard Analytics com Brilho) */
    .analytics-card {
        background: linear-gradient(145deg, #151823 0%, #0f111a 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #232738;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .analytics-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #ff2a2a;
        box-shadow: 0 15px 30px rgba(255, 42, 42, 0.15);
    }

    .card-top-line {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #ff2a2a 0%, #8b0000 100%);
    }

    .kpi-title { color: #8f9bba; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 1px;}
    .kpi-value { color: #ffffff; font-size: 2.2rem; font-weight: 800; line-height: 1.1;}
    .kpi-sub { color: #ff2a2a; font-size: 0.85rem; font-weight: 600; margin-top: 8px;}

    /* Títulos de Seção */
    .section-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 1px solid #1f2333;
        padding-bottom: 10px;
    }

    /* Efeito Hover do Catálogo */
    .product-card { transition: all 0.4s ease; cursor: pointer; }
    .product-card:hover { transform: translateY(-10px); box-shadow: 0 15px 30px rgba(255, 42, 42, 0.2); border-color: #ff2a2a !important; }
</style>
""", unsafe_allow_html=True)

# Função robusta de verificação de imagem
def is_valid_image_url(url):
    if not url or pd.isna(url) or str(url).strip() == "" or str(url) == 'nan': return False
    if not str(url).startswith('http') and not str(url).startswith('//'): return False
    return True

# 3. CARREGAMENTO E TRATAMENTO DE DADOS
@st.cache_data
def carregar_dados():
    arquivos_excel = glob.glob("*.xlsx")
    lista_tabelas = []
    if not arquivos_excel: return pd.DataFrame()
        
    for arquivo in arquivos_excel:
        df_temp = pd.read_excel(arquivo)
        nome_arquivo = arquivo.lower()
        if 'arezzo' in nome_arquivo: marca = 'Arezzo'
        elif 'constance' in nome_arquivo: marca = 'Constance'
        elif 'disantinni' in nome_arquivo: marca = 'Disantinni'
        elif 'santalolla' in nome_arquivo: marca = 'Santa Lolla'
        elif 'sapatella' in nome_arquivo: marca = 'Sapatella'
        elif 'sonhodospes' in nome_arquivo: marca = 'Sonho dos pes'
        elif 'usaflex' in nome_arquivo: marca = 'Usaflex'
        else: marca = 'Outra'
        
        if 'Loja' in df_temp.columns: df_temp = df_temp.rename(columns={'Loja': 'Marca'})
        if 'Marca' not in df_temp.columns: df_temp['Marca'] = marca
        lista_tabelas.append(df_temp)
        
    df = pd.concat(lista_tabelas, ignore_index=True)
    
    if 'Modelo' in df.columns:
        df['Modelo'] = df['Modelo'].astype(str).str.upper().str.strip().str.replace('"', '').str.replace("'", "")
        trocas = {'TENIS': 'TÊNIS', 'SANDALIAS': 'SANDÁLIA', 'SANDALIA': 'SANDÁLIA', 'RASTEIRAS': 'RASTEIRA', 'RASTEIRINHA': 'RASTEIRA'}
        df['Modelo'] = df['Modelo'].replace(trocas)
        
    if 'URL da Imagem' in df.columns:
        df['URL da Imagem'] = df['URL da Imagem'].astype(str).str.replace("https://secure-static.arezzo.com.brhttps://secure-static.arezzo.com.br", "https://secure-static.arezzo.com.br")
    
    if 'Preco' in df.columns: 
        df['Preco'] = pd.to_numeric(df['Preco'], errors='coerce')
        # Criação das Faixas de Preço
        condicoes = [
            (df['Preco'] <= 99.90),
            (df['Preco'] > 99.90) & (df['Preco'] <= 159.90),
            (df['Preco'] > 159.90) & (df['Preco'] <= 199.90),
            (df['Preco'] > 199.90)
        ]
        opcoes = ['P1 - ATÉ R$ 99,90', 'P2 - DE R$ 100 ATÉ R$ 159,90', 'P3 - DE R$ 160 ATÉ R$ 199,90', 'P4 - ACIMA DE R$ 199,90']
        df['Faixa de Preco'] = np.select(condicoes, opcoes, default='Indefinido')
        
    return df

df = carregar_dados()

if df.empty:
    st.error("Nenhuma planilha encontrada na raiz do GitHub. Faça o upload dos arquivos .xlsx.")
else:
    # 4. FILTROS SUPERIORES
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        marcas_disp = sorted(df['Marca'].dropna().unique())
        marca_selecionada = st.selectbox("🎯 Filtrar Coleção/Marca", ["Todas"] + marcas_disp)
        
    with col_filtro2:
        if 'Categoria' in df.columns:
            cats_disp = sorted(df['Categoria'].dropna().astype(str).unique())
            categoria_selecionada = st.selectbox("📂 Filtrar Categoria", ["Todas"] + cats_disp)
        else: categoria_selecionada = "Todas"
        
    with col_filtro3:
         st.write("<br>", unsafe_allow_html=True)
         st.markdown(f"<h3 style='margin:0; padding-top:10px;'>Analytics: <span style='color: #ff2a2a;'>{marca_selecionada}</span></h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    df_filtrado = df.copy()
    if marca_selecionada != "Todas": df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_selecionada]
    if categoria_selecionada != "Todas": df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]

    # 5. CARTÕES DE KPI (Cálculos automáticos)
    kpi_produtos = len(df_filtrado)
    kpi_modelos = df_filtrado['Modelo'].nunique() if 'Modelo' in df_filtrado.columns else 0
    kpi_media = df_filtrado['Preco'].mean()
    
    try: kpi_faixa = df_filtrado['Faixa de Preco'].mode()[0]
    except: kpi_faixa = "N/A"
    
    try: kpi_grupo = df_filtrado['Modelo'].mode()[0]
    except: kpi_grupo = "N/A"

    def gerar_card(titulo, valor, subtitulo=""):
        return f"""<div class="analytics-card"><div class="card-top-line"></div><div class="kpi-title">{titulo}</div><div class="kpi-value">{valor}</div><div class="kpi-sub">{subtitulo}</div></div>"""

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.markdown(gerar_card("Produtos", f"{kpi_produtos}"), unsafe_allow_html=True)
    with col2: st.markdown(gerar_card("Modelo", f"{kpi_modelos}"), unsafe_allow_html=True)
    with col3: st.markdown(gerar_card("Média de Preço", f"R$ {kpi_media:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")), unsafe_allow_html=True)
    with col4: st.markdown(gerar_card("Faixa com Mais Oferta", f"{kpi_faixa.split(' - ')[0]}", kpi_faixa.split(' - ')[-1] if ' - ' in kpi_faixa else ""), unsafe_allow_html=True)
    with col5: st.markdown(gerar_card("Grupo com Mais Oferta", f"{kpi_grupo}"), unsafe_allow_html=True)


    # 6. ABAS DE NAVEGAÇÃO
    aba1, aba2, aba3 = st.tabs(["📈 Visão de Oferta e Preço", "📊 Tabelas de Competitividade", "🛍️ Catálogo Inteligente"])

    # ABA 1: GRÁFICOS
    with aba1:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("<div class='section-title'>Oferta por Grupo (Modelo)</div>", unsafe_allow_html=True)
            df_grupo = df_filtrado['Modelo'].value_counts().reset_index().head(15)
            df_grupo.columns = ['Modelo', 'Quantidade']
            fig1 = px.bar(df_grupo, x='Modelo', y='Quantidade', text='Quantidade', color_discrete_sequence=['#ff2a2a'])
            fig1.update_traces(textposition='outside')
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8f9bba'), xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor='#1f2333', title=""), margin=dict(t=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            st.markdown("<div class='section-title'>Oferta por Faixa de Preço</div>", unsafe_allow_html=True)
            df_faixa = df_filtrado['Faixa de Preco'].value_counts().reset_index()
            df_faixa.columns = ['Faixa', 'Quantidade']
            df_faixa = df_faixa.sort_values(by='Faixa') # Ordena P1, P2, P3, P4
            fig2 = px.bar(df_faixa, x='Faixa', y='Quantidade', text='Quantidade', color_discrete_sequence=['#ff9800'])
            fig2.update_traces(textposition='outside')
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8f9bba'), xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor='#1f2333', title=""), margin=dict(t=10))
            st.plotly_chart(fig2, use_container_width=True)

    # ABA 2: TABELAS DINÂMICAS (PIVOTS)
    with aba2:
        st.markdown("<div class='section-title'>Matriz P1 (Mínimo PV) por Modelo e Marca</div>", unsafe_allow_html=True)
        # Pivot P1 (Min Preço)
        pivot_p1 = pd.pivot_table(df_filtrado, values='Preco', index='Modelo', columns='Marca', aggfunc='min')
        # Formatação de moeda no Streamlit
        st.dataframe(pivot_p1.style.format("R$ {:,.2f}", na_rep="-"), use_container_width=True, height=300)
        
        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1:
            st.markdown("<div class='section-title'>Índice de Competitividade</div>", unsafe_allow_html=True)
            # Cálculo simplificado de IC (Média Sonho dos Pés / Média Concorrentes)
            try:
                media_modelos = df_filtrado.groupby(['Modelo', 'Marca'])['Preco'].mean().unstack()
                if 'Sonho dos pes' in media_modelos.columns:
                    sdp_media = media_modelos['Sonho dos pes']
                    concorrencia_media = media_modelos.drop(columns=['Sonho dos pes']).mean(axis=1)
                    ic_df = (sdp_media / concorrencia_media).reset_index()
                    ic_df.columns = ['Modelo', 'IC Média']
                    ic_df = ic_df.dropna().round(2)
                    st.dataframe(ic_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Sem dados da Sonho dos Pés para calcular IC.")
            except: st.warning("Dados insuficientes para IC.")

        with col_t2:
            st.markdown("<div class='section-title'>Menor Preço por Marca</div>", unsafe_allow_html=True)
            min_preco = df_filtrado.groupby('Marca')['Preco'].min().reset_index()
            min_preco.columns = ['Marca', 'Mínimo de Preço']
            st.dataframe(min_preco.style.format({"Mínimo de Preço": "R$ {:,.2f}"}), use_container_width=True, hide_index=True)

        with col_t3:
            st.markdown("<div class='section-title'>Maior Preço por Marca</div>", unsafe_allow_html=True)
            max_preco = df_filtrado.groupby('Marca')['Preco'].max().reset_index()
            max_preco.columns = ['Marca', 'Máximo de Preço']
            st.dataframe(max_preco.style.format({"Máximo de Preço": "R$ {:,.2f}"}), use_container_width=True, hide_index=True)


    # ABA 3: CATÁLOGO ANIMADO
    with aba3:
        st.markdown("<div class='section-title'>Catálogo de Produtos</div>", unsafe_allow_html=True)
        qtd_mostrar = st.slider("Quantidade a carregar:", min_value=4, max_value=500, value=20, step=4)
        top_produtos = df_filtrado.sort_values(by='Preco').head(qtd_mostrar)
        
        cols = st.columns(4)
        for i, row in top_produtos.reset_index().iterrows():
            with cols[i % 4]:
                url_img = str(row.get('URL da Imagem', '')).strip()
                if url_img.startswith('//'): url_img = 'https:' + url_img
                if not is_valid_image_url(url_img): url_img = "https://via.placeholder.com/300x300.png?text=Erro+Imagem"
                
                nome_modelo = row.get('Modelo', 'N/A')
                nome_marca = row.get('Marca', 'N/A')
                preco_prod = row.get('Preco', 0)
                
                # HTML Minificado do Card com Animação e Fundo Branco para as imagens
                html_card = f"""<div class="product-card" style="position: relative; background-color: #12141d; border-radius: 16px; width: 100%; height: 380px; overflow: hidden; border: 1px solid #232738;"><div style="width: 100%; height: calc(100% - 110px); display: flex; align-items: center; justify-content: center; overflow: hidden; position: absolute; top: 0; left: 0; background-color: #f8fafc;"><img src="{url_img}" referrerpolicy="no-referrer" style="max-width: 90%; max-height: 90%; object-fit: contain;" onerror="this.src='https://via.placeholder.com/300x300.png?text=Quebrado'"></div><div style="position: absolute; bottom: -1px; left: -1px; right: -1px; background: linear-gradient(0deg, rgba(20, 0, 0, 1) 0%, rgba(30, 5, 5, 0.85) 100%); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 0 0 16px 16px; padding: 15px 25px; text-align: left; border-top: 1px solid rgba(255, 42, 42, 0.3); height: 110px; display: flex; flex-direction: column; justify-content: center;"><h4 style="color: #e2e8f0; font-size: 1rem; font-weight: 600; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{nome_modelo}">{nome_modelo}</h4><p style="color: #8f9bba; font-size: 0.8rem; margin: 2px 0 8px 0; font-weight: 600; text-transform: uppercase;">{nome_marca}</p><p style="color: #ff2a2a; font-size: 1.8rem; font-weight: 800; margin: 0; line-height: 1;">R$ {preco_prod:,.2f}</p></div></div><br>"""
                
                st.markdown(html_card, unsafe_allow_html=True)
                
                # HTML minificado e blindado contra Markdown (tudo em uma linha e colado à esquerda)
                html_card = f"""<div class="product-card" style="position: relative; background-color: #1a2233; border-radius: 20px; width: 100%; height: 380px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin-bottom: 20px; border: 1px solid #2d384d;"><div style="width: 100%; height: calc(100% - 110px); display: flex; align-items: center; justify-content: center; overflow: hidden; position: absolute; top: 0; left: 0;"><img src="{url_img}" referrerpolicy="no-referrer" style="max-width: 90%; max-height: 90%; object-fit: contain;" onerror="this.src='https://via.placeholder.com/300x300.png?text=Link+Quebrado'"></div><div style="position: absolute; bottom: -1px; left: -1px; right: -1px; background: linear-gradient(0deg, rgba(11, 15, 25, 1) 0%, rgba(11, 15, 25, 0.7) 100%); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 0 0 20px 20px; padding: 15px 25px 25px 25px; text-align: left; border: 1px solid rgba(255,255,255,0.05); height: 110px; display: flex; flex-direction: column; justify-content: center;"><h4 style="color: #e2e8f0; font-size: 1.1rem; font-weight: 600; margin: 0; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{nome_modelo}">{nome_modelo}</h4><p style="color: #ff9800; font-size: 2rem; font-weight: 800; margin: 0;">R$ {preco_prod:,.2f}</p></div></div>"""
                
                st.markdown(html_card, unsafe_allow_html=True)
