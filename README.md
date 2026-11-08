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
└── out/           # anh ra: 01_..., 02_..., 03_... dung thu tu dong
```

- Chay `make <ten>` khong kem tham so thi doc `titles.txt` va lam lan luot tu tren xuong; so thu tu trong ten anh (`01_`, `02_`) khop so thu tu dong.
- Tieu de dai cu de tren **1 dong**, khong xuong dong; chu tu co cho vua khung.
- Dong bat dau bang `#` va dong trong bi bo qua (dung de ghi chu).
- Moi lan chay tao lai anh tu `01_`. Doi thu tu dong thi xoa `out/` truoc, neu khong anh cu ten cu van con.
- Khong co `titles.txt` va khong truyen `--title`/`--file` thi tool bao loi.

Anh luu o `templates/reddit_post/out/`. Chu tu co theo do dai tieu de; tieu de qua dai se bao loi.

Avatar va nen duoc tao **1 lan** (luc chay dau tien) roi luu `avatar.jpg`, `bg.jpg` trong folder template de dung lai.

| Muon | Them |
|---|---|
| Tao lai avatar | `--new-avatar` |
| Tao lai nen | `--new-bg` |
| Luu tung lop de soi loi | `--debug` (ra `out/_debug/`) |

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

## 5. Them kieu thiet ke moi

1. Copy `templates/reddit_post/` thanh `templates/ten_kieu_moi/`.
2. Thay `original.jpg` bang anh mau cua kieu do; xoa `avatar.jpg`, `bg.jpg`, `out/`.
3. Sua toa do va prompt trong `template.json`.
4. Chay `python -m imgtool make ten_kieu_moi --title "..."`.

## 6. Cau truc

```
imgtool/        code (gflow.py, compose.py, template.py, cli_*.py, fonts/)
templates/      moi kieu thiet ke 1 folder
tests/          python tests/test_compose.py  (chay offline)
```

## 7. Loi thuong gap

| Loi | Cach xu ly |
|---|---|
| `No module named imgtool` | Chua dung trong thu muc `gen Image` |
| `Khong tim thay lenh 'gflow'` | Chua `source .venv/bin/activate` / chua `pip install -r requirements.txt` |
| gflow tra ma loi, khong ra anh | Dang nhap het han: `gflow auth login --browser chrome` |
| `ContentPolicyError` | Flow tu choi prompt (ke ca prompt vo hai). Doi cach mo ta roi chay lai |
| Loi 403 | Tang `--jitter`, vi du `--jitter 10-30`. Neu da tat Xvfb/headless thi chay lai khong headless |
| Chrome van hien len man hinh | Chua cai `xvfb` (muc 4), hoac dang dat `IMGTOOL_SHOW=1` |
