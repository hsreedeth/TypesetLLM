-- shrink-6col.lua   ── keep tables portrait & auto-shrink to text width
-- works on pandoc ≥ 2.10

local Raw = pandoc.RawBlock

-- 1 ▸ inject graphicx once (for \resizebox)
function Meta(meta)
  local hdr = meta['header-includes'] or pandoc.List()
  hdr:insert(Raw('latex', '\\usepackage{graphicx}'))
  meta['header-includes'] = hdr
  return meta
end

-- 2 ▸ width presets (sum to 1.0) for 1–6 columns
local preset = {
  [1] = {1.00},
  [2] = {0.38, 0.62},
  [3] = {0.22, 0.30, 0.48},
  [4] = {0.12, 0.18, 0.30, 0.40},
  [5] = {0.09, 0.13, 0.18, 0.23, 0.37},
  [6] = {0.04, 0.10, 0.12, 0.14, 0.30, 0.30},
}

local function apply_widths(colspecs, widths)
  return colspecs:map(function(cs, i)
    return { cs[1], widths[i] or cs[2] }
  end)
end

-- 3 ▸ wrap every table in \resizebox, adjust col widths if ≤ 6 cols
function Table(tbl)
  local n = #tbl.colspecs
  if n <= 6 then
    tbl.colspecs = apply_widths(tbl.colspecs, preset[n])
  end
  return {
    Raw('latex', '\\resizebox{\\textwidth}{!}{%'),
    tbl,
    Raw('latex', '}% end resizebox')
  }
end

