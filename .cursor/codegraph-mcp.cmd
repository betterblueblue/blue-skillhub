@echo off
setlocal
rem Resolve project root (parent of .cursor/) and pass to codegraph MCP
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
codegraph serve --mcp --path "%ROOT%"
