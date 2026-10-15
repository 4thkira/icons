@echo off
rem Copies the latest 100x100 / 150x150 icons into this folder, rebuilds the gallery, and pushes to GitHub.
cd /d "%~dp0"
python build.py || goto :fail
git add -A
git diff --cached --quiet && (echo. & echo Nothing changed, nothing to publish. & goto :end)
git commit -m "Update icons" || goto :fail
git push || goto :fail
echo.
echo Published! The site updates in a minute or two: https://4thkira.github.io/icons/
goto :end
:fail
echo.
echo Something went wrong - see the messages above.
:end
pause
