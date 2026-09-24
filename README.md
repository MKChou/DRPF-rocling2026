# DRPF-rocling2026

ROCLING 2026 論文 *Deployment Risk Probe Framework (DRPF)* 的可重現性材料。內容對應 camera-ready 的可重現性聲明，只放聲明中寫明釋出的項目。

主表數字受錄音、API 版本與環境差異影響。以自行錄製的音訊重跑，預期得到同結構、非同值的結果。

## 釋出內容

1. **C1 靜音**與 **C2B 取樣清單**
   - `data/c1_silence/`：數位靜音 3/5/8/10 秒各 25 段，共 100 段，16 kHz 單聲道。
   - `data/manifests/c1_silence.csv`
   - `data/manifests/c2b_demand.csv`：DEMAND 五場景（PCAFETER、OHALLWAY、OOFFICE、PRESTO、DLIVING）各 20 段、每段 5 秒的起點清單。
   - `data/c2b/SOURCES.md`：場景對照、授權與 zip SHA-256。C2B 音檔本身不在本倉庫，可依清單自 [DEMAND](https://doi.org/10.5281/zenodo.1227121)（CC BY-SA 3.0）裁切。

2. **計分程式與公開設定**
   - `scripts/text_norm.py`：全形半形、去標點空白、OpenCC `s2twp`，並把 `<{silent}>` 這類標記視為空輸出。
   - `scripts/score_drpf.py`：\(R_{\mathrm{ne}}\)、\(R_{\mathrm{empty}}\)、\(R_{\mathrm{nem}}\)、PCP、KW-ERR。
   - `scripts/vad_gate.py`：Silero VAD，門檻 0.5。
   - `scripts/settings.py`：公開 Whisper `openai/whisper-large-v3-turbo`（語言 `zh`）、邊緣 Nemotron `nvidia/nemotron-3.5-asr-streaming-0.6b`（語言 `zh-CN`）、OpenCC `s2twp`。ACP 的 PCP 觸發詞為論文已寫明的「服藥、插管、急救」。

3. **C3／C4 逐句腳本**
   - `scripts/c3_c4_recording_script.txt`：短答 50 句與猶豫／填充 50 句。

4. **主表聚合計數**
   - `counts/main_table_counts.md`：抄自論文正文與各表，不是本倉庫重算的結果。

## 不在本倉庫

C2A 醫院底噪、語者個人錄音檔、雲端 API 內部 `lang` 細節、Hold-out／金融／法律腳本，以及醫師提供的 C5 腳本與關鍵詞表 \(\mathcal{K}\)。

## 計分

JSONL 每行需有 `ref` 與 `hyp`。否定短答若要計 PCP，加上 `"negated": true`，或用 `--neg-ids` 指定句號。KW-ERR 另需自備詞表，一行一詞。

```powershell
python scripts/score_drpf.py results.jsonl --neg-ids 002,006,009
python scripts/score_drpf.py results.jsonl --keywords my_keywords.txt
```
