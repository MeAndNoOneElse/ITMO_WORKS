В папке CPPO предметы, которые раньше встретил на СППО (англ там)

В папке CYUR предметы, которые раньше встретил на СУиРе в 1 семе только 3

В папке selection лежат всякие разные отборы, которые я писал
# Как сделать ссылку на репозиторий?
- сначала добавляем папку и инициализируем её
  ```bash
  git init
  git remote add origin https://github.com/MeAndNoOneElse/lab_5.git
  git pull --set-upstream origin master
  git push origin master
  ```
- затем из ITMO:
```bash
cd "C:\Users\Eternal Core\OneDrive - MSFT\github_file\ITMO"
git submodule add "../lab_5" "CPPO\old\1-2 Programming\programms\lab_5"
```
  lab_7 это репозиторий, лежит рядом с ITMO (ну или где-то ещё, можно ссылку вставлять), а второй путь это то, где надо создать ссылку
- Удалить, если она уже есть:
 ```bash
 Remove-Item -Recurse -Force "CPPO\old\1-2 Programming\programms\lab_5"
 ```
- Ну и всё:
``` bash
git add .
git commit -m "feat: add Lab_5 as submodule"
git push
```
# Как комитить?
1. Перейдите в папку submodule
```bash
cd CPPO/3_sem/Programming_languages/practics/sea_battle
```
2. Зафиксируйте в репозитории sea_battle
```bash
git add .
git commit -m "Ваши изменения"
git push
```
3. Обновите ссылку в основном репозитории
```bash
cd ../../../../../  # вернуться в ITMO
git add CPPO/3_sem/Programming_languages/practics/sea_battle
git commit -m "Подгузил изменения в основную ветку"
git push
```
4. Перед тем как работать, нужно сделать ```pull``` из папки sea_battle
```bash
cd CPPO/3_sem/Programming_languages/practics/sea_battle
git pull
```
