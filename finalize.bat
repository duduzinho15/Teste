@echo off
echo Finalizing Hotmart removal cleanup...

echo.
echo === Checking for remaining references ===
for %%i in (hotmart perfectpay kiwify) do (
    echo Checking for: %%i
    git grep -nIi "%%i" || echo No references to %%i found
)

echo.
echo === Pushing changes to GitHub ===
git add .
git commit -m "chore: remove Hotmart/PerfectPay/Kiwify; update docs, dashboard and tests"
git push -u origin chore/remove-digital-affiliates

echo.
echo === Cleanup Complete! ===
echo 1. Create a new PR on GitHub
if not "%GITHUB_REPO%"=="" (
    echo    https://github.com/%GITHUB_REPO%/compare/main...chore/remove-digital-affiliates
) else (
    echo    Open your repository on GitHub and create a new PR from chore/remove-digital-affiliates to main
)
echo 2. After PR is merged, run:
echo    git checkout main
echo    git pull
echo    git branch -d chore/remove-digital-affiliates
echo    git push origin --delete chore/remove-digital-affiliates

pause
