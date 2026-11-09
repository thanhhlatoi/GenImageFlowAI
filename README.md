# gen Image

Tao anh tren Google Flow (qua `gflow-cli`, cong cu khong chinh thuc) va dung anh bai dang theo template.

## 1. Cai dat (1 lan)

Can Python 3.12 va Google Chrome.

```bash
cd "gen Image"
bash setup.sh                                      # cai xvfb + venv + thu vien Python
.venv/bin/gflow auth login --browser chrome        # dang nhap Google trong Chrome (chi lan dau)
.venv/bin/gflow auth status                        # phai bao "Flow session verified"
```

`setup.sh` cai `xvfb` bang apt (can sudo, chi hoi mot lan neu chua co), tao `.venv`, roi `pip install -r requirements.txt`.

Moi lan mo terminal moi, chay lai `source .venv/bin/activate` (hoac thay `python` bang `.venv/bin/python`).
Cac lenh ben duoi phai chay **tu thu muc `gen Image`**.

## 2. Tao anh bai dang theo template

```bash
python -m imgtool make reddit_post                       # doc templates/reddit_post/titles.txt
python -m imgtool make reddit_post --title "I Kicked My Sister Out After She Ate My Cake"   # 1 tieu de le
python -m imgtool make reddit_post --file khac.txt       # doc file khac
```

### Luu tieu de: `titles.txt` trong folder cua template

Moi template co file `templates/<ten>/titles.txt` rieng, de cac kieu khong bi lan:

```
templates/reddit_post/
├── titles.txt     # tieu de, moi dong 1 tieu de
├── template.json
└── (anh ra o NasSynology/GenImageFlowAI/<ten>/)  # anh ra: 01_..., 02_..., 03_... dung thu tu dong
```

- Chay `make <ten>` khong kem tham so thi doc `titles.txt` va lam lan luot tu tren xuong; so thu tu trong ten anh (`01_`, `02_`) khop so thu tu dong.
- Tieu de dai cu de tren **1 dong**, khong xuong dong; chu tu co cho vua khung.
- Dong bat dau bang `#` va dong trong bi bo qua (dung de ghi chu).
- Moi lan chay tao lai anh tu `01_`. Doi thu tu dong thi xoa thu muc anh ra truoc, neu khong anh cu ten cu van con.
- Khong co `titles.txt` va khong truyen `--title`/`--file` thi tool bao loi.

Anh luu o `~/Documents/NasSynology/GenImageFlowAI/reddit_post/` (doi bang bien moi truong `IMGTOOL_OUT`). Chu tu co theo do dai tieu de; tieu de qua dai se bao loi.

Avatar va nen duoc tao **1 lan** (luc chay dau tien) roi luu `avatar.jpg`, `bg.jpg` trong folder template de dung lai.

| Muon | Them |
|---|---|
| Tao lai avatar | `--new-avatar` |
| Tao lai nen | `--new-bg` |
| Luu tung lop de soi loi | `--debug` (ra `templates/<ten>/out/_debug/`) |

Doi hinh avatar/nen: sua `avatar_prompt` / `bg_prompt` trong `templates/reddit_post/template.json`, roi chay voi `--new-avatar` / `--new-bg`.

## 3. Tao anh tu prompt (khong qua template)

```bash
python -m imgtool gen "a hot air balloon over Tokyo at sunrise" -n 2 --aspect 16:9
python -m imgtool gen --file prompts.txt --out ./out
```

Tat ca prompt chay trong **1 lan goi gflow** (Chrome chi mo 1 lan). Tuy chon: `-n` (1-4 anh/prompt), `--aspect` (9:16, 16:9, 1:1, 4:3, 3:4), `--model`, `--jitter 3-8` (nghi giua cac prompt, tang len neu bi loi 403).

## 4. Chay an (khong hien Chrome len man hinh)

Flow bat buoc Chrome **co giao dien** (Chrome headless that bi reCAPTCHA chan voi loi 403), nen cach an cua so la chay Chrome trong **man hinh ao Xvfb**.

`bash setup.sh` da cai san. Neu cai tay (khong nam trong `requirements.txt` vi la goi he thong):

```bash
sudo apt install -y xvfb
```

Sau do khong can lam gi them: neu may co `xvfb-run`, moi lenh `make` / `gen` tu chay Chrome trong man hinh ao. Muon xem cua so de go loi:

```bash
IMGTOOL_SHOW=1 python -m imgtool gen --file prompts.txt
```

`gflow auth login` van hien Chrome binh thuong de ban dang nhap.

## 5. Them kieu thiet ke moi (moi kenh 1 template)

1. Copy `templates/reddit_post/` thanh `templates/ten_kieu_moi/`.
2. Thay `original.jpg` bang anh mau cua kieu do; xoa `avatar.jpg`, `bg.jpg`, `out/`.
3. Sua toa do va prompt trong `template.json`.
4. Chay `python -m imgtool make ten_kieu_moi --title "..."`.

## 6. Tao thumbnail cho ca du an tren NAS (titles + batch)

Luu anh mac dinh vao `~/Documents/NasSynology/GenImageFlowAI/` (doi bang bien `IMGTOOL_OUT`). Voi du an co san tren NAS (vd `YouTube/ES/Redit/ES1 404 Cronicas Redditeras`, ten thumbnail cu = tieu de):

```bash
# 1. Quet thumbnail cu, lay ten file lam tieu de -> <du an>/titles.txt (de sua)
python3 -m imgtool titles "<thu muc du an>"          # --force de ghi de, --out de doi noi ghi

# 2. Khai bao template cua kenh (1 lan): <du an>/project.json
echo '{"template": "reddit_post"}' > "<thu muc du an>/project.json"

# 3. Tao thumbnail moi vao new/ canh thumbnail cu
python3 -m imgtool batch "<thu muc du an>"           # --template ten, --force lam lai
```

- `titles.txt`: moi dong `duong/dan/thumbnail cu | tieu de`. Chi sua phan SAU dau `|`. Dong bat dau `#` hoac xoa dong de bo qua tap do.
- Anh moi: `<thu muc thumbnail cu>/new/<ten cu>.png`. Tap nao da co anh trong `new/` thi bo qua. Loi o 1 tieu de khong lam dung ca lo.
- Moi kenh 1 template rieng trong `templates/` (xem muc 8), moi du an tro toi template bang `project.json`.

## 7. [TODO] Doi tieu de bang 9router (Codex): lenh `rewrite`

Chua lam. Y tuong: them buoc nam giua `titles` va `batch`:

```
titles  ->  titles.txt  ->  rewrite (9router/Codex)  ->  titles.txt da doi  ->  batch
```

Cach hoat dong:
1. 9router chay tren may nhu proxy tuong thich OpenAI (thuong `http://localhost:20128/v1`, can API key). Tool goi `POST /chat/completions` voi model Codex da cau hinh trong 9router.
2. Doc tung dong `duong dan | tieu de`, gui tieu de cu kem prompt mau (vd "Viet lai tieu de Reddit nay bang tieng Tay Ban Nha, giu y, hap dan hon, toi da N ky tu"), nhan tieu de moi. Co the gui nhieu tieu de trong 1 request cho nhanh va do ton quota.
3. Khong ghi de mat ban cu: giu ca hai, vd `Tap1/Old.jpg | Tieu de moi | # cu: Old title`, hoac ghi ra `titles_new.txt` de xem va sua tay truoc khi chay `batch`.
4. Chay lai thi dong da viet lai duoc bo qua (`--force` de lam lai).

Nen co:
- Prompt rieng moi kenh: `templates/<ten>/rewrite_prompt.txt` (moi kenh giong va ngon ngu khac nhau).
- Gioi han do dai tieu de lay tu template (chu tu co nhung tieu de qua dai se bao loi).
- Cau hinh qua bien moi truong `ROUTER_URL`, `ROUTER_KEY`, `ROUTER_MODEL`; khong ghi cung key vao code.

Can quyet dinh khi lam:
- URL 9router va ten model Codex dang dung (key de trong bien moi truong, khong gui vao chat).
- Muc dich doi: dich sang ngon ngu khac, lam hap dan hon, hay rut gon?
- 1 phuong an cho moi tieu de, hay 3 phuong an de chon?

## 8. Cau truc

```
imgtool/        code (gflow.py, compose.py, template.py, paths.py, cli_*.py, fonts/)
templates/      moi kieu thiet ke 1 folder
tests/          python tests/test_compose.py  (chay offline)
```

## 9. Loi thuong gap

| Loi | Cach xu ly |
|---|---|
| `No module named imgtool` | Chua dung trong thu muc `gen Image` |
| `Khong tim thay lenh 'gflow'` | Chua `source .venv/bin/activate` / chua `pip install -r requirements.txt` |
| gflow tra ma loi, khong ra anh | Dang nhap het han: `gflow auth login --browser chrome` |
| `ContentPolicyError` | Flow tu choi prompt (ke ca prompt vo hai). Doi cach mo ta roi chay lai |
| Loi 403 | Tang `--jitter`, vi du `--jitter 10-30`. Neu da tat Xvfb/headless thi chay lai khong headless |
| Chrome van hien len man hinh | Chua cai `xvfb` (muc 4), hoac dang dat `IMGTOOL_SHOW=1` |
