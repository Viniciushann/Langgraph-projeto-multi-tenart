-- ============================================================================
-- FUNÇÃO: match_documents - Busca vetorial com filtro multi-tenant
-- ============================================================================
-- Esta função DEVE ser executada no Supabase DEV SQL Editor
--
-- IMPORTANTE: Esta função garante isolamento de dados entre tenants!
-- Cada tenant só pode ver seus próprios documentos.
-- ============================================================================

CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5,
    filter_tenant_id uuid DEFAULT NULL
)
RETURNS TABLE(
    id uuid,
    content text,
    metadata jsonb,
    tenant_id uuid,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        d.tenant_id,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM conhecimento_dev d
    WHERE
        -- FILTRO CRÍTICO: Apenas documentos do tenant especificado
        (filter_tenant_id IS NULL OR d.tenant_id = filter_tenant_id)
        AND
        -- Threshold de similaridade
        1 - (d.embedding <=> query_embedding) > match_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================================
-- COMENTÁRIOS
-- ============================================================================

COMMENT ON FUNCTION match_documents IS 'Busca documentos por similaridade vetorial com filtro multi-tenant obrigatório para isolamento de dados';

-- ============================================================================
-- TESTES
-- ============================================================================

-- Teste 1: Buscar documentos sem filtro de tenant (deve retornar todos)
-- SELECT * FROM match_documents(
--     query_embedding := (SELECT embedding FROM conhecimento_dev LIMIT 1),
--     match_threshold := 0.5,
--     match_count := 10,
--     filter_tenant_id := NULL
-- );

-- Teste 2: Buscar documentos de um tenant específico
-- SELECT * FROM match_documents(
--     query_embedding := (SELECT embedding FROM conhecimento_dev LIMIT 1),
--     match_threshold := 0.5,
--     match_count := 10,
--     filter_tenant_id := '9605db82-51bf-4101-bdb0-ba73c5843c43'::uuid
-- );

-- ============================================================================
-- VALIDAÇÃO DE ISOLAMENTO (CRÍTICO!)
-- ============================================================================

-- Este teste deve retornar 0 documentos de outros tenants
-- SELECT COUNT(*) FROM match_documents(
--     query_embedding := (SELECT embedding FROM conhecimento_dev LIMIT 1),
--     match_threshold := 0.0,
--     match_count := 1000,
--     filter_tenant_id := 'tenant-1-id'::uuid
-- ) WHERE tenant_id != 'tenant-1-id'::uuid;
--
-- Resultado esperado: 0

-- ============================================================================
-- INSTRUÇÕES DE USO
-- ============================================================================

-- 1. Copie todo este arquivo
-- 2. Acesse Supabase DEV em: https://wmzhbgcqugtctnzyinqw.supabase.co
-- 3. Vá em "SQL Editor" no menu lateral
-- 4. Clique em "New Query"
-- 5. Cole este código
-- 6. Clique em "Run" para executar
-- 7. Verifique que a função foi criada com sucesso

-- ============================================================================
