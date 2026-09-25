-- Give ordinary tables useful portrait widths and rotate only genuinely wide
-- tables. Pandoc's LaTeX writer emits longtable, so headers repeat naturally
-- when a table spans multiple pages.

local function latex(value)
  return pandoc.RawBlock("latex", value)
end

local landscape_start = "\\begin{landscape}\\begingroup\\scriptsize\\setlength{\\tabcolsep}{1.5pt}"
local landscape_end = "\\endgroup\\end{landscape}"
local wide_tables = 0

local function cell_text(cell)
  return pandoc.utils.stringify(cell.contents or cell)
end

local function visit_rows(tbl, callback)
  for _, row in ipairs(tbl.head.rows) do callback(row) end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.head) do callback(row) end
    for _, row in ipairs(body.body) do callback(row) end
  end
  for _, row in ipairs(tbl.foot.rows) do callback(row) end
end

local function looks_numeric(value)
  local compact = value:gsub("%s+", "")
  return compact == "" or compact:match("^[%+%-]?[%d%.,%%<>=%()–—/]+$") ~= nil
end

local function measured_widths(tbl)
  local count = #tbl.colspecs
  local longest = {}
  local numeric = {}
  for index = 1, count do
    longest[index] = 6
    numeric[index] = true
  end

  visit_rows(tbl, function(row)
    for index, cell in ipairs(row.cells) do
      local value = cell_text(cell)
      longest[index] = math.max(longest[index], #value)
      if value ~= "" and not looks_numeric(value) then numeric[index] = false end
    end
  end)

  local wide = count >= 7
  local weights = {}
  local total = 0
  for index = 1, count do
    local cap = numeric[index] and 12 or (wide and 20 or 34)
    local weight = math.max(wide and 10 or 7, math.min(longest[index], cap))
    if index == 1 and not numeric[index] then
      weight = math.max(weight, wide and 18 or 12)
    end
    weights[index] = weight
    total = total + weight
  end

  local budget = wide and 0.90 or 0.94
  for index = 1, count do weights[index] = budget * weights[index] / total end
  return weights, total
end

function Table(tbl)
  local count = #tbl.colspecs
  local widths, content_score = measured_widths(tbl)

  tbl.colspecs = tbl.colspecs:map(function(colspec, index)
    return {colspec[1], widths[index]}
  end)

  local needs_landscape = count >= 7 or (count >= 6 and content_score > 95)
  if needs_landscape then
    wide_tables = wide_tables + 1
    return {
      latex(landscape_start),
      tbl,
      latex(landscape_end),
    }
  end
  return tbl
end

function Pandoc(doc)
  if wide_tables ~= 1 then return doc end

  local prose_length = 0
  for _, block in ipairs(doc.blocks) do
    if block.t ~= "Table" and block.t ~= "RawBlock" then
      prose_length = prose_length + #pandoc.utils.stringify(block)
    end
  end
  if prose_length > 180 then return doc end

  -- A compact document centered on one wide table reads better on a single
  -- landscape page than with title and closing sentence stranded separately.
  local blocks = pandoc.List({latex(landscape_start)})
  for _, block in ipairs(doc.blocks) do
    if block.t ~= "RawBlock" or (block.text ~= landscape_start and block.text ~= landscape_end) then
      blocks:insert(block)
    end
  end
  blocks:insert(latex(landscape_end))
  doc.blocks = blocks
  return doc
end
