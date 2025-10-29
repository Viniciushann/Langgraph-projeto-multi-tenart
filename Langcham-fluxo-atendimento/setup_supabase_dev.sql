-- ========================================
-- SETUP SUPABASE PARA AMBIENTE DEV
-- ========================================
-- Executar este script no Supabase SQL Editor
-- ========================================

-- ========== TABELA DE CLIENTES DEV ==========
CREATE TABLE IF NOT EXISTS clients_dev (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT,
    telefone TEXT UNIQUE NOT NULL,
    email TEXT,
    empresa TEXT,
    dados_adicionais JSONB DEFAULT '{}'::jsonb,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_clients_dev_telefone ON clients_dev(telefone);
CREATE INDEX IF NOT EXISTS idx_clients_dev_criado_em ON clients_dev(criado_em DESC);

-- Comentários
COMMENT ON TABLE clients_dev IS 'Tabela de clientes para ambiente DEV';
COMMENT ON COLUMN clients_dev.telefone IS 'Número de telefone no formato internacional (ex: 5562999999999)';

-- ========== HISTÓRICO DE CONVERSAS DEV ==========
CREATE TABLE IF NOT EXISTS conversation_history_dev (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients_dev(id) ON DELETE CASCADE,
    mensagem TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    tipo_mensagem TEXT CHECK (tipo_mensagem IN ('texto', 'audio', 'imagem', 'video', 'documento'))
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_conversation_dev_client_id ON conversation_history_dev(client_id);
CREATE INDEX IF NOT EXISTS idx_conversation_dev_timestamp ON conversation_history_dev(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_dev_role ON conversation_history_dev(role);

-- Comentários
COMMENT ON TABLE conversation_history_dev IS 'Histórico de mensagens para ambiente DEV';
COMMENT ON COLUMN conversation_history_dev.role IS 'user = cliente, assistant = bot, system = sistema';

-- ========== BASE DE CONHECIMENTO DEV ==========
-- Habilitar extensão pgvector se ainda não estiver ativa
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS conhecimento_dev (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embeddings dimension
    metadata JSONB DEFAULT '{}'::jsonb,
    categoria TEXT,
    tags TEXT[],
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para performance e busca vetorial
CREATE INDEX IF NOT EXISTS idx_conhecimento_dev_embedding ON conhecimento_dev
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_conhecimento_dev_categoria ON conhecimento_dev(categoria);
CREATE INDEX IF NOT EXISTS idx_conhecimento_dev_ativo ON conhecimento_dev(ativo);
CREATE INDEX IF NOT EXISTS idx_conhecimento_dev_tags ON conhecimento_dev USING GIN(tags);

-- Comentários
COMMENT ON TABLE conhecimento_dev IS 'Base de conhecimento vetorizada para RAG (DEV)';
COMMENT ON COLUMN conhecimento_dev.embedding IS 'Vetor de 1536 dimensões gerado por OpenAI';

-- ========== FUNÇÃO PARA BUSCA SEMÂNTICA DEV ==========
CREATE OR REPLACE FUNCTION buscar_conhecimento_dev(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    titulo TEXT,
    conteudo TEXT,
    similarity FLOAT,
    metadata JSONB,
    categoria TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.titulo,
        c.conteudo,
        1 - (c.embedding <=> query_embedding) AS similarity,
        c.metadata,
        c.categoria
    FROM conhecimento_dev c
    WHERE
        c.ativo = true
        AND 1 - (c.embedding <=> query_embedding) > match_threshold
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Comentários
COMMENT ON FUNCTION buscar_conhecimento_dev IS 'Busca semântica na base de conhecimento DEV usando similaridade de cosseno';

-- ========== TRIGGER PARA ATUALIZAR TIMESTAMP ==========
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger às tabelas
CREATE TRIGGER update_clients_dev_updated_at
    BEFORE UPDATE ON clients_dev
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conhecimento_dev_updated_at
    BEFORE UPDATE ON conhecimento_dev
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========== DADOS DE EXEMPLO PARA TESTES ==========

-- Cliente de teste
INSERT INTO clients_dev (nome, telefone, email, empresa, dados_adicionais)
VALUES (
    'Cliente Teste DEV',
    '5562999999999',
    'teste@dev.com',
    'Empresa Teste',
    '{"origem": "teste_dev", "versao": "1.0"}'::jsonb
) ON CONFLICT (telefone) DO NOTHING;

-- Base de conhecimento de teste
INSERT INTO conhecimento_dev (titulo, conteudo, categoria, tags, metadata)
VALUES
    (
        'Teste DEV - Horário de Atendimento',
        'Este é um ambiente de desenvolvimento. Horário de testes: 24/7',
        'atendimento',
        ARRAY['teste', 'dev', 'horario'],
        '{"ambiente": "dev", "tipo": "teste"}'::jsonb
    ),
    (
        'Teste DEV - Serviços',
        'Ambiente DEV para testar funcionalidades do bot WhatsApp com LangGraph',
        'servicos',
        ARRAY['teste', 'dev', 'servicos'],
        '{"ambiente": "dev", "tipo": "teste"}'::jsonb
    )
ON CONFLICT DO NOTHING;

-- ========== POLÍTICAS RLS (Row Level Security) ==========
-- Desabilitar RLS para DEV (facilitar testes)
ALTER TABLE clients_dev DISABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_history_dev DISABLE ROW LEVEL SECURITY;
ALTER TABLE conhecimento_dev DISABLE ROW LEVEL SECURITY;

-- ========== GRANTS ==========
-- Dar permissões ao role anon (usado pela API)
GRANT ALL ON clients_dev TO anon;
GRANT ALL ON conversation_history_dev TO anon;
GRANT ALL ON conhecimento_dev TO anon;

GRANT EXECUTE ON FUNCTION buscar_conhecimento_dev TO anon;

-- ========== VIEWS ÚTEIS PARA DEBUG ==========

-- View para ver últimas conversas
CREATE OR REPLACE VIEW ultimas_conversas_dev AS
SELECT
    c.nome AS cliente,
    c.telefone,
    ch.mensagem,
    ch.role,
    ch.tipo_mensagem,
    ch.timestamp
FROM conversation_history_dev ch
JOIN clients_dev c ON ch.client_id = c.id
ORDER BY ch.timestamp DESC
LIMIT 100;

GRANT SELECT ON ultimas_conversas_dev TO anon;

-- View para estatísticas
CREATE OR REPLACE VIEW stats_dev AS
SELECT
    (SELECT COUNT(*) FROM clients_dev) AS total_clientes,
    (SELECT COUNT(*) FROM conversation_history_dev) AS total_mensagens,
    (SELECT COUNT(*) FROM conhecimento_dev WHERE ativo = true) AS total_conhecimento,
    (SELECT COUNT(DISTINCT client_id) FROM conversation_history_dev) AS clientes_ativos,
    NOW() AS data_consulta;

GRANT SELECT ON stats_dev TO anon;

-- ========================================
-- VERIFICAÇÃO FINAL
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '✅ Setup DEV concluído com sucesso!';
    RAISE NOTICE '📊 Tabelas criadas:';
    RAISE NOTICE '   - clients_dev';
    RAISE NOTICE '   - conversation_history_dev';
    RAISE NOTICE '   - conhecimento_dev';
    RAISE NOTICE '🔍 Funções criadas:';
    RAISE NOTICE '   - buscar_conhecimento_dev()';
    RAISE NOTICE '📈 Views criadas:';
    RAISE NOTICE '   - ultimas_conversas_dev';
    RAISE NOTICE '   - stats_dev';
    RAISE NOTICE '✅ Dados de teste inseridos';
END $$;

-- Verificar estatísticas
SELECT * FROM stats_dev;

-- ========================================
-- COMANDOS ÚTEIS PARA TESTES
-- ========================================

-- Ver todos os clientes
-- SELECT * FROM clients_dev;

-- Ver últimas conversas
-- SELECT * FROM ultimas_conversas_dev;

-- Ver estatísticas
-- SELECT * FROM stats_dev;

-- Buscar na base de conhecimento (exemplo)
-- SELECT * FROM buscar_conhecimento_dev(
--     query_embedding := (SELECT embedding FROM conhecimento_dev LIMIT 1),
--     match_threshold := 0.5,
--     match_count := 3
-- );

-- Limpar todos os dados (CUIDADO!)
-- TRUNCATE TABLE conversation_history_dev, clients_dev, conhecimento_dev CASCADE;
