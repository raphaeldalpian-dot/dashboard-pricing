import streamlit as st
import pandas as pd
import plotly.express as px
import glob

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Inteligência Competitiva", layout="wide", initial_sidebar_state="collapsed")

# 2. INJEÇÃO DE CSS CUSTOMIZADO (Design Nível Executivo)
st.markdown("""
<style>
    /* Fundo principal escuro profundo */
    .stApp { background-color: #161c24; }
    
    h1, h2, h3, p, span { color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stSidebar {visibility: hidden;}

    /* Seção de Filtros Superior */
    .filter-section {
        background-color: #212b36;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 1px solid #323d48;
    }

    /* Cards Personalizados Modernos */
    .custom-card {
        background-color: #212b36;
        border: 1px solid #323d48;
        padding: 20px;
        border-radius: 12px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(236, 163, 50, 0.1);
    }

    .card-icon { font-size: 2.5rem; margin-right: 15px; width: 50px; text-align: center; }
    .card-data { flex: 1; }
    .card-title { color: #919eab; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .card-value { color: #f8fafc; font-size: 1.8rem; font-weight: bold; }
    
    /* Cores de destaque */
    .card-pink { border-left: 5px solid #ff0080; }
    .card-green { border-left: 5px solid #00e676; }
    .card-orange { border-left: 5px solid #ff9800; }
    .card-blue { border-left: 5px solid #2979ff; }
    
    .icon-pink { color: #ff0080; }
    .icon-green { color: #00e676; }
    .icon-orange { color: #ff9800; }
    .icon-blue { color: #2979ff; }

    /* Efeito hover para o card de produto */
    .product-card { transition: transform 0.3s ease; }
    .product-card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(236, 163, 50, 0.15); }
</style>
""", unsafe_allow_html=True)

# Função robusta de verificação de imagem
def is_valid_image_url(url):
    if not url or pd.isna(url) or str(url).strip() == "" or str(url) == 'nan':
        return False
    if not str(url).startswith('http') and not str(url).startswith('//'):
        return False
    return True

# 3. CARREGAMENTO E LIMPEZA DE DADOS
@st.cache_data
def carregar_dados():
    arquivos_excel = glob.glob("*.xlsx")
    lista_tabelas = []
    
    if not arquivos_excel:
        return pd.DataFrame()
        
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
        trocas = {'TENIS': 'TÊNIS', 'SANDALIAS': 'SANDÁLIA', 'SANDALIA': 'SANDÁLIA', 'RASTEIRAS': 'RASTEIRA', 'RASTEIRINHA': 'RASTEIRA', 'SAPATILHAS': 'SAPATILHA', 'TAMANCOS': 'TAMANCO', 'CINTOS': 'CINTO', 'BOLSAS': 'BOLSA', 'BOTAS': 'BOTA', 'PANTUFA': 'CHINELO', 'CHINELOS': 'CHINELO', 'ÓCULO': 'ÓCULOS', 'MULES': 'MULE', 'MOCASSINS': 'MOCASSIM'}
        df['Modelo'] = df['Modelo'].replace(trocas)
        
    if 'URL da Imagem' in df.columns:
        # Corrige a URL duplicada da Arezzo
        df['URL da Imagem'] = df['URL da Imagem'].astype(str).str.replace(
            "https://secure-static.arezzo.com.brhttps://secure-static.arezzo.com.br", 
            "https://secure-static.arezzo.com.br"
        )
    if 'Preco' in df.columns: df['Preco'] = pd.to_numeric(df['Preco'], errors='coerce')
        
    return df

df = carregar_dados()

if df.empty:
    st.error("Nenhum arquivo Excel encontrado na pasta. Coloque as planilhas na mesma pasta do script Dashboard.py.")
else:
    # 4. MENU SUPERIOR DE FILTROS
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            marcas_disponiveis = sorted(df['Marca'].dropna().unique())
            marca_selecionada = st.selectbox("🎯 Marca", ["Todas"] + marcas_disponiveis)
            
        with col_filtro2:
            if 'Categoria' in df.columns:
                categorias_disponiveis = sorted(df['Categoria'].dropna().astype(str).unique())
                categoria_selecionada = st.selectbox("📂 Categoria", ["Todas"] + categorias_disponiveis)
            else: categoria_selecionada = "Todas"
            
        with col_filtro3:
             st.write("<br>", unsafe_allow_html=True)
             st.markdown(f"<h3 style='margin:0; padding-top:10px;'>Competitor Intel: <span style='color: #ECA332;'>{marca_selecionada}</span></h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    df_filtrado = df.copy()
    if marca_selecionada != "Todas": df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_selecionada]
    if categoria_selecionada != "Todas": df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]

    # 5. CARTÕES DE KPI (HTML minificado para evitar erros)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    def criar_cartao(titulo, valor, cor_accent, icone_hex):
        return f"""<div class="custom-card card-{cor_accent}"><div class="card-icon icon-{cor_accent}">&#x{icone_hex};</div><div class="card-data"><div class="card-title">{titulo}</div><div class="card-value">{valor}</div></div></div>"""

    with col1:
        st.markdown(criar_cartao("📦 Produtos", f"{len(df_filtrado)}", "pink", "f1b2"), unsafe_allow_html=True)
    with col2:
        st.markdown(criar_cartao("🏷️ Preço Mínimo", f"R$ {df_filtrado['Preco'].min():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "green", "f3d1"), unsafe_allow_html=True)
    with col3:
        st.markdown(criar_cartao("📊 Preço Médio", f"R$ {df_filtrado['Preco'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "orange", "f080"), unsafe_allow_html=True)
    with col4:
        st.markdown(criar_cartao("💎 Preço Máximo", f"R$ {df_filtrado['Preco'].max():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "blue", "f013"), unsafe_allow_html=True)
    
    with col5:
        if marca_selecionada != "Sonho dos pes" and not df.empty:
            preco_min_sdp = df[df['Marca'] == 'Sonho dos pes']['Preco'].min()
            media_conc = df_filtrado['Preco'].mean()
            if pd.notna(preco_min_sdp) and media_conc > 0:
                ic_val = f"{preco_min_sdp / media_conc:.2f}"
                st.markdown(criar_cartao("⚖️ IC vs SDP", ic_val, "pink", "f201"), unsafe_allow_html=True)
            else: 
                st.markdown(criar_cartao("⚖️ IC vs SDP", "N/A", "pink", "f201"), unsafe_allow_html=True)
        else: 
            st.markdown(criar_cartao("⚖️ IC vs SDP", "-", "pink", "f201"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. GRÁFICOS E CATÁLOGO
    aba1, aba2 = st.tabs(["📊 Visão Geral do Mercado", "🛍️ Catálogo Inteligente"])

    with aba1:
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            oferta_modelo = df_filtrado['Modelo'].value_counts().reset_index()
            oferta_modelo.columns = ['Modelo', 'Quantidade']
            
            fig1 = px.bar(oferta_modelo.head(15), x='Modelo', y='Quantidade', 
                          title="Share de Oferta por Modelo (Top 15)",
                          color_discrete_sequence=['#ff0080']) 
            
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor='#1f2937', title="")
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_grafico2:
            top_modelos = oferta_modelo.head(8)['Modelo'].tolist()
            df_top_modelos = df_filtrado[df_filtrado['Modelo'].isin(top_modelos)]
            
            fig2 = px.box(df_top_modelos, x='Modelo', y='Preco', 
                          title="Dispersão de Preços (Boxplot)",
                          color_discrete_sequence=['#00e676']) 
            
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor='#1f2937', title="Preço (R$)")
            )
            st.plotly_chart(fig2, use_container_width=True)

    with aba2:
        st.markdown(f"### Catálogo de Produtos: {marca_selecionada}")
        
        qtd_mostrar = st.slider("Quantidade de produtos para carregar:", min_value=4, max_value=500, value=20, step=4)
        top_produtos = df_filtrado.sort_values(by='Preco').head(qtd_mostrar)
        
        cols = st.columns(4)
        for i, row in top_produtos.reset_index().iterrows():
            with cols[i % 4]:
                url_img = str(row.get('URL da Imagem', '')).strip()
                
                if url_img.startswith('//'): url_img = 'https:' + url_img
                    
                if not is_valid_image_url(url_img):
                    url_img = "https://via.placeholder.com/300x300.png?text=Sem+Imagem+no+Excel"
                
                nome_modelo = row.get('Modelo', 'N/A')
                preco_prod = row.get('Preco', 0)
                
                # HTML minificado e blindado contra Markdown (tudo em uma linha e colado à esquerda)
                html_card = f"""<div class="product-card" style="position: relative; background-color: #1a2233; border-radius: 20px; width: 100%; height: 380px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin-bottom: 20px; border: 1px solid #2d384d;"><div style="width: 100%; height: calc(100% - 110px); display: flex; align-items: center; justify-content: center; overflow: hidden; position: absolute; top: 0; left: 0;"><img src="{url_img}" referrerpolicy="no-referrer" style="max-width: 90%; max-height: 90%; object-fit: contain;" onerror="this.src='https://via.placeholder.com/300x300.png?text=Link+Quebrado'"></div><div style="position: absolute; bottom: -1px; left: -1px; right: -1px; background: linear-gradient(0deg, rgba(11, 15, 25, 1) 0%, rgba(11, 15, 25, 0.7) 100%); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 0 0 20px 20px; padding: 15px 25px 25px 25px; text-align: left; border: 1px solid rgba(255,255,255,0.05); height: 110px; display: flex; flex-direction: column; justify-content: center;"><h4 style="color: #e2e8f0; font-size: 1.1rem; font-weight: 600; margin: 0; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{nome_modelo}">{nome_modelo}</h4><p style="color: #ff9800; font-size: 2rem; font-weight: 800; margin: 0;">R$ {preco_prod:,.2f}</p></div></div>"""
                
                st.markdown(html_card, unsafe_allow_html=True)