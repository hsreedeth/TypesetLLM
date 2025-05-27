-- landscape-6col.lua  ─── rotate all tables + width presets up to 6 cols
-- pandoc ≥ 2.10

local function latex(str) return pandoc.RawBlock('latex', str) end

-- 1 ▸ make sure pdflscape is loaded only once
function Meta(meta)
  local h = meta['header-includes'] or pandoc.List()
  h:insert(latex('\\usepackage{pdflscape}'))
  meta['header-includes'] = h
  return meta
end

-- 2 ▸ width presets (sums = 1.00)
local preset = {
  [1] = {1.00},
  [2] = {0.38, 0.62},
  [3] = {0.22, 0.30, 0.48},
  [4] = {0.12, 0.18, 0.30, 0.40},
  [5] = {0.09, 0.13, 0.18, 0.23, 0.37},
  [6] = {0.04, 0.10, 0.12, 0.14, 0.30, 0.30},
}

-- 3 ▸ helper to copy alignment while injecting width
local function apply_widths(colspecs, widths)
  return colspecs:map(function (cs, i)
    return {cs[1], widths[i] or cs[2]}   -- fall back if preset shorter
  end)
end

-- 4 ▸ process every table
function Table(tbl)
  local n = #tbl.colspecs
  if n <= 6 then
    tbl.colspecs = apply_widths(tbl.colspecs, preset[n])
  end
  -- wrap in landscape block
  return { latex('\\begin{landscape}'), tbl, latex('\\end{landscape}') }
end
