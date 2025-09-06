@echo off
echo === Final Cleanup Script ===

:: 1. Check for remaining references
echo.
echo === Checking for remaining references ===
for %%i in (hotmart perfectpay kiwify) do (
    echo Checking for: %%i
    git grep -nIi "%%i" || echo No references to %%i found
)

:: 2. Run tests and linting
echo.
echo === Running tests and linting ===
call .venv\Scripts\activate
python -m pytest -q || (
    echo Tests failed. Please fix the issues before continuing.
    pause
    exit /b 1
)

ruff check src || (
    echo Linting failed. Please fix the issues before continuing.
    pause
    exit /b 1
)

:: 3. Add and commit changes
echo.
echo === Creating commit ===
git add .
git commit -m "chore: remove Hotmart/PerfectPay/Kiwify; organize scripts; update docs and tests" || (
    echo No changes to commit or commit failed.
    pause
    exit /b 1
)

:: 4. Push to remote
echo.
echo === Pushing to remote ===
git push -u origin chore/remove-digital-affiliates || (
    echo Push failed. Please check your Git configuration and try again.
    pause
    exit /b 1
)

echo.
echo === Cleanup Complete! ===
echo 1. Open your repository on GitHub
echo 2. Click on "Compare & pull request"
echo 3. Use this PR title and description:
echo.
echo "chore: remove Hotmart/PerfectPay/Kiwify; organize scripts; update docs and tests"
echo.
echo "Changes:"
echo "- Removed Hotmart, PerfectPay, and Kiwify references"
echo "- Updated documentation and tests"
echo "- Organized scripts in tools/maintenance"
echo.
echo "Validation:"
echo "- All tests pass"
echo "- Linting passes"
echo "- No remaining references to removed services"
echo.
echo 4. After PR is merged, run:
echo    git checkout main
echo    git pull
echo    git branch -d chore/remove-digital-affiliates
echo    git push origin --delete chore/remove-digital-affiliates

pause
