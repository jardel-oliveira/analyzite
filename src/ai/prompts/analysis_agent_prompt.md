---
title: Prompt — Gerador de analysis_plan.json
tags: [prompt, survey, analytics, pandas, streamlit]
---

# Prompt: Gerador de analysis_plan.json

Você receberá um `survey_schema.json` com a estrutura de um questionário de pesquisa.

Sua tarefa é gerar um `analysis_plan.json`.

---

## Objetivo

Criar KPIs estratégicos, métricas derivadas, cruzamentos analíticos e códigos Python/Pandas executáveis para cada KPI relevante, com base exclusivamente nas perguntas disponíveis no `survey_schema.json`.

---

## Contexto técnico obrigatório

O `analysis_plan.json` será importado em um app Streamlit que executa o campo `python_pandas_code` usando um DataFrame chamado `df`.
O executor do app exige que cada bloco de código defina obrigatoriamente uma variável final chamada `result`.
Se o código não definir `result`, o KPI falhará.

---

## Regras gerais

1. Use somente perguntas existentes no JSON.
2. Use os campos `question_type`, `analytical_role`, `options_observed`, `example_values` e `suggested_kpis` como insumo principal.
3. Proponha apenas KPIs coerentes com o texto da pergunta e com seu papel analítico.
4. O código Python deve assumir que existe um DataFrame chamado `df`.
5. Não invente colunas inexistentes.
6. Use sempre o texto exato da coluna presente no schema quando referenciar colunas do DataFrame.
7. Retorne JSON válido, sem explicações, sem comentários e sem texto fora do JSON.
8. Cada KPI deve conter obrigatoriamente:
   - `id`
   - `name`
   - `description`
   - `based_on_questions`
   - `analytical_role`
   - `chart_suggestion`
   - `output_type`
   - `formula_logic`
   - `python_pandas_code`

---

## Preferências de visualização

1. Nunca use `chart_suggestion = "pie"`. Substitua sempre por `"bar"`.
2. Para gráficos de barras, use sempre orientação vertical: categorias no eixo X, valores no eixo Y.
3. Ao nomear colunas do `result` em gráficos de barra, use sempre `['categoria', 'percentual']` ou `['categoria', 'valor']`.

---

## Regras obrigatórias para python_pandas_code

1. O código deve sempre terminar com uma variável chamada `result`.
2. Nunca use `value` como variável final.
3. Nunca use `import`.
4. Nunca use `open`, `exec`, `eval`, `compile`, `input`, `__import__`, `os`, `sys`, `subprocess`, `pathlib`, `requests`, `pickle` ou qualquer acesso a arquivos, rede ou sistema.
5. Use apenas pandas já disponível como `pd` e o DataFrame `df`.
6. O código deve ser autocontido, curto e executável.
7. Sempre trate nulos antes de calcular métricas.
8. Sempre use `.copy()` ao criar bases intermediárias filtradas.
9. Evite regex complexa, exceto quando realmente necessária.
10. Não use bibliotecas externas.
11. Não use variáveis não definidas no próprio bloco.
12. Para percentuais, prefira retornar valores de 0 a 100.
13. Para tabelas de distribuição, devolva percentuais arredondados com `.round(2)`.
14. Sempre normalize strings com `.str.strip().str.lower()` antes de comparações.
15. Use nomes de variáveis intermediárias descritivos e únicos por KPI (ex: `col_kpi001`, `base_kpi001`) para evitar colisões de escopo.

---

## Contrato obrigatório entre chart_suggestion e result

### `scorecard`
O `result` deve ser um escalar: `int`, `float` ou string curta.
```python
result = float(base[col].eq('sim').mean() * 100)
```

### `table`
O `result` pode ser: `DataFrame`, `Series`, `dict`, `list` ou escalar.

### `bar`
O `result` deve ser **OBRIGATORIAMENTE** um DataFrame com exatamente 2 colunas:
- primeira coluna → categoria (string)
- segunda coluna → valor numérico

> Nunca retorne mais ou menos de 2 colunas para `chart_suggestion = "bar"`.

### `stacked_bar`
O `result` deve ser **OBRIGATORIAMENTE** um DataFrame em formato longo com exatamente 3 colunas:
- primeira coluna → categoria principal
- segunda coluna → série
- terceira coluna → valor numérico

---

## Regras analíticas

1. Quando fizer cruzamentos, use no máximo uma pergunta de corte por KPI.
2. Para perguntas abertas, proponha apenas análises exploratórias:
   - volume de respostas
   - exemplos de respostas
   - frequência de termos simples, somente se possível sem `import`
3. Não proponha KPI estratégico para perguntas sem valor analítico claro.
4. Prefira KPIs acionáveis e legíveis em dashboard.
5. Evite redundância. Não crie vários KPIs quase idênticos.

---

## Regras por tipo de pergunta

### `single_choice`
Pode gerar distribuição, ranking, participação percentual, cortes simples.

### `multiple_choice`
Pode gerar frequência de menções, taxa de seleção e ranking de opções.
Quando necessário, dividir respostas por `';'`.

### `scale`
Pode gerar média, top2box, bottom2box, distribuição e comparação por corte.

### `open_text`
Pode gerar volume, exemplos e contagem de preenchimento.
Evite NLP avançado.

---

## Regras de naming

1. Use ids no padrão `kpi_001`, `kpi_002`, `kpi_003`.
2. Use nomes curtos, claros e executivos.
3. `description` deve explicar a utilidade do KPI.
4. `formula_logic` deve descrever a lógica em linguagem natural.

---

## Campo study_title

O campo `study_title` no JSON de saída deve ser extraído diretamente do campo `"study_title"` presente no `survey_schema.json` recebido.

---

## Formato obrigatório de saída
```json
{
  "study_title": "...",
  "kpis": [
    {
      "id": "kpi_001",
      "name": "...",
      "description": "...",
      "based_on_questions": ["q001_..."],
      "analytical_role": "...",
      "chart_suggestion": "bar|stacked_bar|scorecard|table",
      "output_type": "percentage|count|mean|distribution|text_summary",
      "formula_logic": "...",
      "python_pandas_code": "..."
    }
  ]
}
```

---

## Exemplos corretos de python_pandas_code

### Exemplo 1 — Scorecard percentual
```python
col_kpi001 = 'Você possui cartão Smiles?'
base_kpi001 = df[df[col_kpi001].notna()].copy()
result = float(
    base_kpi001[col_kpi001].astype(str).str.strip().str.lower().eq('sim').mean() * 100
)
```

### Exemplo 2 — Gráfico de barras vertical
```python
col_kpi002 = 'Qual a sua faixa de idade?'
base_kpi002 = df[df[col_kpi002].notna()].copy()
result = (
    base_kpi002[col_kpi002]
    .astype(str)
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
    .reset_index()
)
result.columns = ['categoria', 'percentual']
```

### Exemplo 3 — Gráfico empilhado
```python
cut_col_kpi003 = 'Qual a sua faixa de idade?'
kpi_col_kpi003 = 'Você possui cartão Smiles?'
base_kpi003 = df[df[cut_col_kpi003].notna() & df[kpi_col_kpi003].notna()].copy()
result = (
    base_kpi003.groupby([cut_col_kpi003, kpi_col_kpi003])
    .size()
    .reset_index(name='valor')
)
result.columns = ['categoria', 'serie', 'valor']
```

### Exemplo 4 — Tabela simples
```python
col_kpi004 = 'Quais benefícios você considera mais importantes?'
base_kpi004 = df[df[col_kpi004].notna()].copy()
exploded_kpi004 = (
    base_kpi004[col_kpi004]
    .astype(str)
    .str.split(';')
    .explode()
    .str.strip()
)
result = (
    exploded_kpi004.value_counts()
    .reset_index()
)
result.columns = ['opcao', 'frequencia']
```

---

## Restrições finais

1. Nunca gere `python_pandas_code` sem `result`.
2. Nunca use `import`.
3. Nunca use código fora do JSON.
4. Nunca invente coluna.
5. Nunca use `chart_suggestion = "pie"`.
6. Sempre respeite o formato exigido por `chart_suggestion`.
7. Para `chart_suggestion = "bar"`, o `result` deve ter **exatamente 2 colunas**: categoria e valor numérico.
8. Se um KPI não puder ser implementado com segurança e clareza, não o inclua.