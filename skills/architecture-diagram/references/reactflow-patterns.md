# React Flow Architecture Diagram Patterns

## CDN Setup (import maps + esm.sh)

React Flow runs in standalone HTML without a build step using esm.sh import maps and htm (tagged template literals instead of JSX).

```html
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@18.3.1",
    "react-dom": "https://esm.sh/react-dom@18.3.1",
    "react-dom/client": "https://esm.sh/react-dom@18.3.1/client",
    "react/jsx-runtime": "https://esm.sh/react@18.3.1/jsx-runtime",
    "@xyflow/react": "https://esm.sh/@xyflow/react@12.6.0?external=react,react-dom",
    "htm": "https://esm.sh/htm@3.1.1"
  }
}
</script>
<link rel="stylesheet" href="https://esm.sh/@xyflow/react@12.6.0/dist/style.css">
```

**Critical:** You MUST include both `react-dom` AND `react-dom/client` in the import map. The `@xyflow/react` package imports `react-dom` internally. Missing it causes a blank page with a module resolution error.

## Module Imports

```js
import React, { useState, useCallback, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import htm from 'htm';
import {
  ReactFlow, Background, Controls, MiniMap,
  useNodesState, useEdgesState, Handle, Position
} from '@xyflow/react';

const html = htm.bind(React.createElement);
```

## Color Palette

```js
const palette = {
  ui:       { bg: '#7C3AED', bgLight: '#EDE9FE', border: '#6D28D9' },  // Violet
  agent:    { bg: '#4F46E5', bgLight: '#EEF2FF', border: '#3730A3' },  // Indigo
  gateway:  { bg: '#EA580C', bgLight: '#FFF7ED', border: '#C2410C' },  // Orange
  mcp:      { bg: '#0891B2', bgLight: '#ECFEFF', border: '#0E7490' },  // Cyan
  external: { bg: '#059669', bgLight: '#ECFDF5', border: '#047857' },  // Emerald
  data:     { bg: '#DC2626', bgLight: '#FEF2F2', border: '#B91C1C' },  // Red
};
```

Group containers use the `bgLight` value as background and the node color as border:
- Agent groups: `bgColor: '#EEF2FF', borderColor: '#818CF8'`
- MCP groups: `bgColor: '#ECFEFF', borderColor: '#22D3EE'`
- External groups: `bgColor: '#ECFDF5', borderColor: '#34D399'`

## SVG Icon Library

All icons are inline SVGs — no external dependencies. Stroke-based, 24x24 viewBox, white on colored background.

```js
const icons = {
  chat: html`<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,

  agent: html`<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>`,

  subagent: html`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/><path d="M12 1v5M12 18v5M1 12h5M18 12h5"/></svg>`,

  gateway: html`<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v5M12 18v5M4.22 4.22l3.54 3.54M16.24 16.24l3.54 3.54M1 12h5M18 12h5M4.22 19.78l3.54-3.54M16.24 7.76l3.54-3.54"/></svg>`,

  server: html`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><circle cx="6" cy="6" r="1"/><circle cx="6" cy="18" r="1"/></svg>`,

  cloud: html`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>`,

  database: html`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,

  key: html`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>`,
};
```

To add new icons, use Lucide icon SVG paths at 24x24 viewBox with `stroke="currentColor"`.

## Custom Node Components

### ArchNode — Icon card with label

White card, colored icon box, text label below. Invisible handles for clean presentation.

```js
function ArchNode({ data }) {
  const p = palette[data.nodeType] || palette.mcp;
  const icon = icons[data.icon] || icons.server;

  const style = {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    gap: '6px', padding: '12px 16px',
    background: '#FFFFFF',
    border: '2px solid ' + p.border,
    borderRadius: '10px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
    minWidth: '100px',
    position: 'relative',
  };
  const iconBg = {
    width: '44px', height: '44px',
    borderRadius: '10px', background: p.bg,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: '#FFFFFF',
  };
  const labelStyle = {
    fontSize: '11px', fontWeight: '600', color: '#1E293B',
    textAlign: 'center', lineHeight: '1.3',
    fontFamily: 'Inter, system-ui, sans-serif',
  };

  return html`
    <div style=${style}>
      <${Handle} type="target" position=${Position.Top}
        style=${{ background: 'transparent', width: 1, height: 1, border: 'none', top: -1 }} />
      <div style=${iconBg}>${icon}</div>
      <div style=${labelStyle}>${data.label}</div>
      <${Handle} type="source" position=${Position.Bottom}
        style=${{ background: 'transparent', width: 1, height: 1, border: 'none', bottom: -1 }} />
    </div>
  `;
}
```

### GroupNode — Dashed container with floating label

```js
function GroupNode({ data }) {
  const style = {
    width: '100%', height: '100%',
    background: data.bgColor || '#F8FAFC',
    border: '2px dashed ' + (data.borderColor || '#CBD5E1'),
    borderRadius: '12px',
    padding: '8px',
  };
  const labelStyle = {
    position: 'absolute', top: '-12px', left: '16px',
    background: '#FFFFFF', padding: '2px 10px',
    fontSize: '12px', fontWeight: '700', color: '#475569',
    fontFamily: 'Inter, system-ui, sans-serif',
    borderRadius: '4px',
    border: '1px solid ' + (data.borderColor || '#CBD5E1'),
  };

  return html`
    <div style=${style}>
      <div style=${labelStyle}>${data.label}</div>
    </div>
  `;
}

const nodeTypes = { arch: ArchNode, group: GroupNode };
```

## Node Definitions

### Standalone node
```js
{ id: 'ui', type: 'arch', position: { x: 380, y: 0 },
  data: { label: 'Chat UI', icon: 'chat', nodeType: 'ui' } }
```

### Group container
Groups need explicit `style: { width, height }`. React Flow does NOT auto-size groups.
```js
{ id: 'grp-agents', type: 'group', position: { x: 200, y: 120 },
  style: { width: 520, height: 200 },
  data: { label: 'Agent Platform', bgColor: '#EEF2FF', borderColor: '#818CF8' } }
```

### Child inside a group
Child positions are **relative to the group's top-left corner**.
```js
{ id: 'base-agent', type: 'arch', position: { x: 20, y: 40 },
  parentId: 'grp-agents',
  data: { label: 'Base Agent', icon: 'agent', nodeType: 'agent' } }
```

### Multi-line labels
Use `\n` in labels for wrapping:
```js
data: { label: 'Service\nOperator', icon: 'subagent', nodeType: 'agent' }
```

## Edge Definitions

### Standard labeled edge
```js
{ id: 'e1', source: 'ui', target: 'base-agent',
  label: 'SSE streaming',
  style: { stroke: '#7C3AED' },
  labelStyle: { fontSize: 11, fontFamily: 'Inter', fontWeight: 500, fill: '#475569' },
  labelBgStyle: { fill: '#fff', fillOpacity: 0.9 } }
```

### Dashed/animated edge (async connections)
```js
{ id: 'e6', source: 'cred-vault', target: 'litellm',
  label: 'OAuth tokens', animated: true,
  style: { stroke: '#DC2626', strokeDasharray: '6 3' },
  labelStyle: { fontSize: 11, fontFamily: 'Inter', fontWeight: 500, fill: '#DC2626' },
  labelBgStyle: { fill: '#fff', fillOpacity: 0.9 } }
```

### Unlabeled edge (fan-out patterns)
When many edges go from one source to many targets, label only one:
```js
{ id: 'e7', source: 'litellm', target: 'mcp-gdrive', style: { stroke: '#94A3B8' } },
{ id: 'e8', source: 'litellm', target: 'mcp-gmail', style: { stroke: '#94A3B8' } },
{ id: 'e10', source: 'litellm', target: 'mcp-qb',
  label: 'MCP routing', style: { stroke: '#94A3B8' },
  labelStyle: { fontSize: 11, fontFamily: 'Inter', fontWeight: 500, fill: '#475569' },
  labelBgStyle: { fill: '#fff', fillOpacity: 0.9 } },
```

### Intra-group edges (within a container)
Use color matching the group's accent:
```js
{ id: 'e2', source: 'base-agent', target: 'task-builder',
  label: 'delegates', type: 'smoothstep',
  style: { stroke: '#818CF8' },
  labelStyle: { fontSize: 10, fontFamily: 'Inter', fontWeight: 500, fill: '#6366F1' },
  labelBgStyle: { fill: '#EEF2FF', fillOpacity: 0.9 } }
```

## App Component and Mount

```js
function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return html`
    <${ReactFlow}
      nodes=${nodes}
      edges=${edges}
      onNodesChange=${onNodesChange}
      onEdgesChange=${onEdgesChange}
      nodeTypes=${nodeTypes}
      fitView
      fitViewOptions=${{ padding: 0.15 }}
      defaultEdgeOptions=${{ type: 'smoothstep', animated: false }}
      proOptions=${{ hideAttribution: true }}
    >
      <${Background} color="#E2E8F0" gap=${20} size=${1} />
      <${Controls} position="bottom-left" />
      <${MiniMap}
        nodeColor=${(n) => {
          const t = n.data?.nodeType;
          return palette[t]?.bg || '#CBD5E1';
        }}
        style=${{ border: '1px solid #E2E8F0', borderRadius: '8px' }}
      />
    <//>
  `;
}

const root = createRoot(document.getElementById('app'));
root.render(html`<${App} />`);
```

## HTML Shell (header + legend + mount point)

```html
<div id="header">
  <h1><!-- TITLE --></h1>
  <p><!-- SUBTITLE --></p>
</div>
<div id="app"></div>
<div id="legend">
  <h3>Legend</h3>
  <div class="legend-item"><div class="legend-dot" style="background:#7C3AED"></div> UI</div>
  <div class="legend-item"><div class="legend-dot" style="background:#4F46E5"></div> Agent</div>
  <!-- ... one per node type used ... -->
</div>
```

Required CSS:
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', system-ui, sans-serif; background: #FFFFFF; }
#header { padding: 20px 32px 14px; border-bottom: 1px solid #E2E8F0; }
#header h1 { font-size: 22px; font-weight: 700; color: #0F172A; margin-bottom: 2px; }
#header p { font-size: 13px; color: #64748B; }
#app { width: 100vw; height: calc(100vh - 68px); }
#legend {
  position: fixed; bottom: 16px; right: 16px;
  background: white; border: 1px solid #E2E8F0; border-radius: 8px;
  padding: 10px 14px; font-size: 11px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08); z-index: 100;
}
.react-flow__node { font-family: 'Inter', system-ui, sans-serif; }
.react-flow__attribution { display: none; }
```

## Layout Strategy

React Flow does NOT have automatic layout. Position nodes manually using a grid strategy:

1. **Top-to-bottom hierarchy**: UI at y=0, groups below in 200-250px increments
2. **Horizontal centering**: Center the widest layer, align narrower layers to its midpoint
3. **Group children**: Space at ~110-130px horizontal intervals, y=35-40 inside group
4. **Group sizing**: Width = (numChildren * 110) + padding. Height = ~140-200px

Typical y-coordinates for a 5-layer architecture:
- Row 1 (UI): y=0
- Row 2 (Agent group): y=120
- Row 3 (Infrastructure): y=400
- Row 4 (MCP group): y=560
- Row 5 (External group): y=780

## Serving and Viewing

```bash
npx -y serve /tmp/architecture-diagram -p 8789 --no-clipboard &
```

Navigate: `mcp__chrome-devtools__navigate_page` to `http://localhost:8789/diagram.html`
Screenshot: `mcp__chrome-devtools__take_screenshot`

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blank page, header/legend visible | JS module error | Check `list_console_messages` — likely missing `react-dom` in import map |
| Nodes render but no edges | Edge source/target IDs don't match node IDs | Verify IDs match exactly (case-sensitive) |
| Group doesn't contain children | Missing `parentId` on child nodes | Add `parentId: 'group-id'` to each child |
| Group too small for children | Explicit `style.width/height` too small | Increase group dimensions |
| First load is slow/blank | esm.sh cold start | Reload the page — subsequent loads are fast |
