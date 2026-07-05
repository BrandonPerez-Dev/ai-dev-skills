#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const TOOL_MAP = {
  'Bash': '"*"',
  'Read': 'read_file',
  'Write': 'write_file',
  'Edit': 'replace',
  'Glob': 'glob',
  'Grep': 'grep_search',
  'LS': 'list_directory'
};

const MODEL_MAP = {
  'sonnet': 'gemini-3.1-pro-preview',
  'opus': 'gemini-3.1-pro-preview',
  'haiku': 'gemini-3-flash-preview'
};

function copyRecursiveSync(src, dest) {
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
  for (const item of fs.readdirSync(src)) {
    const srcPath = path.join(src, item);
    const destPath = path.join(dest, item);
    if (fs.statSync(srcPath).isDirectory()) {
      copyRecursiveSync(srcPath, destPath);
    } else {
      fs.writeFileSync(destPath, fs.readFileSync(srcPath));
    }
  }
}

function processAgentContent(content) {
  const frontmatterRegex = /^---\n([\s\S]*?)\n---(\n[\s\S]*)$/;
  const match = content.match(frontmatterRegex);
  if (!match) return content;

  let [_, frontmatter, body] = match;

  // 1. Map Tools
  const toolsRegex = /tools:\n((?:\s+- [A-Za-z]+\n)+)/g;
  frontmatter = frontmatter.replace(toolsRegex, (m, toolList) => {
    let newTools = "tools:\n";
    const tools = toolList.match(/- ([A-Za-z]+)/g) || [];
    tools.forEach(t => {
      const toolName = t.replace('- ', '');
      const geminiTool = TOOL_MAP[toolName] || '"*"'; 
      newTools += `  - ${geminiTool}\n`;
    });
    return newTools;
  });

  // 2. Map Models
  for (const [claudeModel, geminiModel] of Object.entries(MODEL_MAP)) {
    frontmatter = frontmatter.replace(new RegExp(`model:\\s+${claudeModel}\\b`, 'g'), `model: ${geminiModel}`);
  }

  // 3. Clean up Claude-specific fields
  // Remove disallowedTools entirely along with its list
  frontmatter = frontmatter.replace(/^disallowedTools:\s*\n(?:\s+- .+\n)*/gm, '');
  // Remove memory field
  frontmatter = frontmatter.replace(/^memory:.*\n?/gm, '');

  return `---\n${frontmatter.trim()}\n---${body}`;
}

function syncAgents(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return;
  if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });

  for (const file of fs.readdirSync(srcDir)) {
    if (!file.endsWith('.md')) continue;
    
    const srcPath = path.join(srcDir, file);
    const destPath = path.join(destDir, file);
    
    const content = fs.readFileSync(srcPath, 'utf8');
    const translated = processAgentContent(content);
    
    fs.writeFileSync(destPath, translated);
    console.log(`Synced Agent: ${file}`);
  }
}

function syncSkills(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return;
  copyRecursiveSync(srcDir, destDir);
  console.log(`Synced Skills: ${srcDir} -> ${destDir}`);
}

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("Usage: node sync-gemini.js <source-dir> <target-dir>");
  console.error("Example: node sync-gemini.js .claude .gemini");
  process.exit(1);
}

const srcBase = args[0];
const destBase = args[1];

syncAgents(path.join(srcBase, 'agents'), path.join(destBase, 'agents'));
syncSkills(path.join(srcBase, 'skills'), path.join(destBase, 'skills'));

console.log('Sync complete.');
