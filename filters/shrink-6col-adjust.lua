-- shrink-6col-adjust.lua  ─ resize longtables safely with adjustbox
local Raw = pandoc.RawBlock

-- 1 ▸ inject adjustbox once
function Meta(meta)
  local hdr = meta['header-includes'] or pandoc.List()
  hdr:insert(Raw('latex', '\\usepackage{adjustbox}'))
  meta['header-includes'] = hdr
  return meta
end

-- 2 ▸ width presets for ≤ 6 columns
local preset = {
  [1]={1},[2]={0.38,0.62},[3]={0.22,0.30,0.48},
  [4]={0.12,0.18,0.30,0.40},
  [5]={0.09,0.13,0.18,0.23,0.37},
  [6]={0.04,0.10,0.12,0.14,0.30,0.30},
}

local function apply(cs,widths)
  return cs:map(function(c,i) return {c[1], widths[i] or c[2]} end)
end

-- 3 ▸ wrap each table in adjustbox
function Table(tbl)
  local n = #tbl.colspecs
  if n<=6 then tbl.colspecs = apply(tbl.colspecs,preset[n]) end
  return {
    Raw('latex','\\begin{adjustbox}{max width=\\textwidth}%'),
    tbl,
    Raw('latex','\\end{adjustbox}')
  }
end
