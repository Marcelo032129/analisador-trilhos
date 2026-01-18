import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules.data_loader import load_data
from modules.filters import criar_filtros, aplicar_filtros

# Configuração da página
st.set_page_config(
    page_title="Análise do Simulador de Trilho",
    page_icon="🛤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .upload-info {
        background-color: #EFF6FF;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<p class="main-header">🛤️ Analisador de Trilhos - Sistema de Priorização</p>', unsafe_allow_html=True)

# ===== SEÇÃO DE UPLOAD MELHORADA =====
st.sidebar.markdown("## 📤 Upload de Dados")

# Opção principal: upload de arquivo
uploaded_file = st.sidebar.file_uploader(
    "**Carregue seu arquivo Excel**", 
    type=['xlsx', 'xls'],
    help="Formato esperado: arquivo exportado do Simulador de Trilhos"
)

# Mostrar informações sobre o formato
with st.sidebar.expander("📋 Formato do arquivo"):
    st.write("""
    **Colunas necessárias:**
    - `Gerência`: Unidade operacional
    - `Classe`: Classificação (A, B, C, D, E)
    - `DV Atual`: Desgaste Vertical
    - `DH Atual`: Desgaste Horizontal
    - `Equipamento`: Identificador
    
    **Colunas opcionais:**
    - `Data da Prospecção`
    - `Restrição Via (Motivo)`
    - `Backlog`
    - `Extensão`
    """)

# ===== VERIFICAR SE TEM ARQUIVO =====
if uploaded_file is None:
    # Tela inicial - sem arquivo
    st.markdown("""
    <div class="upload-info">
        <h3>👋 Bem-vindo ao Analisador de Trilhos!</h3>
        <p>Este sistema ajuda a priorizar intervenções em trilhos ferroviários baseado em dados técnicos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Como funciona:")
        st.write("""
        1. **Carregue** seu arquivo Excel na sidebar
        2. **Filtre** por gerência, classe ou criticidade
        3. **Visualize** métricas e gráficos
        4. **Priorize** intervenções com base no score
        5. **Exporte** a lista de prioridades
        """)
    
    with col2:
        st.markdown("### 🎯 Benefícios:")
        st.write("""
        ✅ **Priorização automática** de trechos críticos  
        ✅ **Dashboard interativo** com filtros dinâmicos  
        ✅ **Análise visual** com gráficos intuitivos  
        ✅ **Exportação** para CSV para compartilhamento  
        ✅ **Compatível** com dados do Simulador de Trilhos
        """)
    
    # Mostrar exemplo de dados
    if st.checkbox("📋 Ver exemplo de dados esperados"):
        exemplo_df = pd.DataFrame({
            'Equipamento': ['12/040448-040470tg', '29/064622-064870tg'],
            'Gerência': ['UP SERRAS', 'UP RS'],
            'Classe': ['A (P2)', 'A (P2)'],
            'DV Atual': [203, 115],
            'DH Atual': [2, 6],
            'Nível Crítico': ['Alta', 'Média'],
            'Score Prioridade': [152.1, 58.5]
        })
        st.dataframe(exemplo_df, use_container_width=True)
    
    st.stop()  # Para aqui se não tem arquivo

# ===== CARREGAMENTO DE DADOS =====
with st.spinner('Processando arquivo...'):
    df = load_data(uploaded_file)

# Verificar se temos dados
if df.empty:
    st.error("❌ Não foi possível processar o arquivo. Verifique o formato.")
    st.stop()

st.success(f"✅ **{len(df)}** registros carregados com sucesso!")

# ===== FILTROS =====
filtros = criar_filtros(df)
df_filtrado = aplicar_filtros(df, filtros)

# Mostrar estatísticas na sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Estatísticas")
st.sidebar.markdown(f"**Total:** {len(df):,} registros")
st.sidebar.markdown(f"**Filtrados:** {len(df_filtrado):,} registros")

if 'Gerência' in df_filtrado.columns and len(df_filtrado) > 0:
    st.sidebar.markdown(f"**Gerências:** {df_filtrado['Gerência'].nunique()}")

# ===== MÉTRICAS =====
st.markdown('<p class="sub-header">📊 Métricas do Projeto</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Trechos Analisados", f"{len(df_filtrado):,}")

with col2:
    if 'Nível Crítico' in df_filtrado.columns:
        criticos = len(df_filtrado[df_filtrado['Nível Crítico'] == 'Alta'])
        st.metric("Críticos (Alta)", f"{criticos:,}")

with col3:
    if 'DV Atual' in df_filtrado.columns and not df_filtrado['DV Atual'].isna().all():
        avg_dv = df_filtrado['DV Atual'].mean()
        st.metric("DV Médio", f"{avg_dv:.1f}")

with col4:
    if 'Score Prioridade' in df_filtrado.columns:
        max_score = df_filtrado['Score Prioridade'].max()
        st.metric("Maior Score", f"{max_score:.1f}")

# ===== ABAS PRINCIPAIS =====
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🚨 Priorização", "📋 Dados"])

with tab1:
    st.markdown('<p class="sub-header">📊 Análise Visual</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Classe' in df_filtrado.columns and len(df_filtrado) > 0:
            df_classe = df_filtrado.copy()
            df_classe['Classe'] = df_classe['Classe'].astype(str)
            df_classe = df_classe[~df_classe['Classe'].isin(['nan', 'NÃO INFORMADO', ''])]
            
            if len(df_classe) > 0:
                fig1 = px.pie(df_classe, names='Classe', title='Distribuição por Classe',
                             color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("ℹ️ Sem dados de classe para exibir")
    
    with col2:
        if 'Nível Crítico' in df_filtrado.columns and len(df_filtrado) > 0:
            fig2 = px.bar(df_filtrado, x='Nível Crítico', 
                         title='Distribuição por Nível Crítico',
                         color='Nível Crítico', 
                         color_discrete_map={'Alta': '#DC2626', 'Média': '#F59E0B', 'Baixa': '#10B981'},
                         labels={'count': 'Quantidade'})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("ℹ️ Sem dados de criticidade para exibir")

with tab2:
    st.markdown('<p class="sub-header">🚨 Lista de Prioridades</p>', unsafe_allow_html=True)
    
    if len(df_filtrado) > 0:
        # Ordenar por prioridade
        if 'Score Prioridade' in df_filtrado.columns:
            df_priorizado = df_filtrado.sort_values('Score Prioridade', ascending=False).head(50)
            st.info(f"📋 Mostrando os **50 trechos mais críticos** de {len(df_filtrado)} total")
        else:
            df_priorizado = df_filtrado.head(50)
        
        # Colunas para mostrar
        colunas = []
        for col in ['Equipamento', 'Gerência', 'Classe', 'Nível Crítico', 'DV Atual', 'Score Prioridade']:
            if col in df_priorizado.columns:
                colunas.append(col)
        
        # Adicionar número de sequência
        df_display = df_priorizado[colunas].copy()
        df_display.insert(0, '#', range(1, len(df_display) + 1))
        
        st.dataframe(df_display, use_container_width=True, height=500)
        
        # Botões de exportação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button('📥 Exportar Top 50 (CSV)', type='primary'):
                csv = df_priorizado.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="Clique para baixar",
                    data=csv,
                    file_name=f"priorizacao_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    key='download_csv'
                )
        
        with col2:
            if st.button('📋 Exportar Todos Filtrados'):
                csv_all = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="Baixar todos filtrados",
                    data=csv_all,
                    file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    key='download_all'
                )
    else:
        st.warning("⚠️ Nenhum dado disponível após filtragem")

with tab3:
    st.markdown('<p class="sub-header">📋 Dados Completos</p>', unsafe_allow_html=True)
    
    st.write(f"**Arquivo carregado:** {uploaded_file.name}")
    st.write(f"**Total de registros:** {len(df):,}")
    st.write(f"**Após filtros:** {len(df_filtrado):,}")
    
    if len(df_filtrado) > 0:
        # Seletor de colunas
        todas_colunas = df_filtrado.columns.tolist()
        colunas_selecionadas = st.multiselect(
            "Selecione colunas para visualizar:",
            todas_colunas,
            default=todas_colunas[:8] if len(todas_colunas) > 8 else todas_colunas
        )
        
        if colunas_selecionadas:
            st.dataframe(df_filtrado[colunas_selecionadas].head(100), 
                        use_container_width=True, 
                        height=400)
            
            # Estatísticas
            with st.expander("📊 Estatísticas Descritivas"):
                if 'DV Atual' in df_filtrado.columns:
                    st.write("**Desgaste Vertical (DV Atual):**")
                    st.dataframe(df_filtrado['DV Atual'].describe().to_frame().T)
                
                if 'Score Prioridade' in df_filtrado.columns:
                    st.write("**Score de Prioridade:**")
                    st.dataframe(df_filtrado['Score Prioridade'].describe().to_frame().T)
        else:
            st.info("👈 Selecione pelo menos uma coluna para visualizar")
    else:
        st.info("📭 Nenhum dado para exibir após filtragem")

# ===== RODAPÉ =====
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>
    <p>📅 {datetime.now().strftime("%d/%m/%Y %H:%M")} | 🛠️ Analisador de Trilhos v2.0 | 
    <a href="https://streamlit.io" target="_blank">Powered by Streamlit</a></p>
    <p style="font-size: 0.8rem; margin-top: 10px;">
    Sistema de priorização de manutenção ferroviária | Desenvolvido para análise técnica
    </p>
</div>
""", unsafe_allow_html=True)
