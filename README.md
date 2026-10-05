# KSMS AR큐브 v2

스마트폰/태블릿/PC 카메라로 종이 큐브를 비추면 면마다 AR 이미지를 보여주는 웹앱.

## 실행

- PC: `KSMS AR큐브.exe` 더블클릭 (Edge 앱 창으로 실행)
- 직접 주소: `https://localhost:8445` (serve_https.py 실행 필요)
- GitHub Pages: 저장소 Settings > Pages에서 배포 후 `https://<계정>.github.io/<저장소>/` 접속

## 구조

- `index.html` — 앱 전체 (AR.js + Three.js)
- `cube/` — 큐브 면(c0/h0/j0/s0/k0/m0.jpg) + 인쇄용 전개도
- `ar/` — 면별 AR 표시 이미지 (jpg 우선, 없으면 png)
- `markers/` — 면별 인식 데이터 (.patt, cube_fix 기준 생성)
- `vendor/`, `data/` — AR.js 라이브러리 및 카메라 파라미터
- `serve_https.py`, `cert.pem`, `key.pem` — 로컬 HTTPS 서버용
- `launcher.py` — exe 소스
- `_make_faces_v3.py`, `_make_markers.py` — 면/마커 재생성 스크립트
