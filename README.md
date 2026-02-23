# 🛠️ Fusion 360 Customization Pack

개인적으로 Fusion 360 작업 효율을 높이기 위해 추가한 커스터마이징 모음입니다.  
누구나 쉽게 적용할 수 있도록 정리했습니다.

---

## 📦 포함된 내용

### 1. 기본 단축키 설정 (Fusion 360 내장 기능)
Fusion 360에 이미 있지만 단축키가 없던 기능들에 단축키를 할당했습니다.

| 단축키 | 기능 |
|--------|------|
| `X` | 활성 컴포넌트 전환 (Activate Component) |
| `Alt + C` | 컴포넌트 생성 (Create Component) |
| *(그 외 본인 취향에 맞게 추가)* | |

> Fusion 360 상단 메뉴 → **파일 > 환경설정 > 단축키**에서 직접 설정합니다.

---

### 2. AnyShortcut 플러그인
Fusion 360에서 기본 API로는 단축키 등록이 안 되는 기능들을 지원하는 서드파티 플러그인입니다.

- **다운로드**: [AnyShortcut 공식 사이트](https://anyshortcut.app) 또는 검색
- **설치 방법**:
  1. `AnyShortcut_win64.msi` 실행
  2. 설치 후 Fusion 360 재시작
  3. 상단 메뉴에 AnyShortcut 탭 생성됨
  4. 원하는 커맨드에 단축키 할당

---

### 3. 커스텀 Add-Ins (직접 제작)

Fusion 360 API로 만든 애드인들입니다. `AddIns/` 폴더에 있습니다.

#### 📁 AddIns 목록

| 애드인 | 단축키 | 기능 |
|--------|--------|------|
| `ToggleComponentVisibility` | `V` | 선택한 본체의 **상위 컴포넌트 전체**를 숨기기/보이기 토글 |
| `SelectActiveComponent` | `Ctrl+Shift+A` | 현재 활성화된 컴포넌트를 브라우저에서 선택 |
| `ActivateRootShortCut` | `Shift+X` | 최상위(Root) 컴포넌트 선택 (이후 `X`로 활성화) |
| `BrowserNavigateShortcut` | `Ctrl+Shift+N` | 브라우저에서 스케치 폴더까지 자동 탐색 (→↓↓↓→) |
| `ExpandSketchesShortcut` | `Ctrl+Shift+S` | 현재 컴포넌트의 Sketches 폴더를 브라우저에서 확장 |

---

## 🚀 Add-Ins 설치 방법

### 방법 1: 폴더 복사 (권장)

1. 이 저장소를 클론하거나 ZIP으로 다운로드
   ```
   git clone https://github.com/hanbhgjop/aphelion-nadir.git
   ```

2. `AddIns` 폴더 안의 원하는 애드인 폴더를 아래 경로에 복사:
   ```
   C:\Users\[사용자명]\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\
   ```

3. Fusion 360 실행 → **도구 탭 > 추가 기능 > 스크립트 및 추가 기능**

4. 해당 애드인을 찾아서 **실행** 또는 **자동 실행** 체크

### 방법 2: Fusion 360 내에서 직접 로드

1. Fusion 360 상단 메뉴 → **도구 > 추가 기능 > 스크립트 및 추가 기능**
2. **내 스크립트** 탭 → 오른쪽 `+` 버튼 → 애드인 폴더 선택
3. 실행 버튼 클릭

---

## ⚠️ 주의사항

- 단축키 충돌 시 Fusion 360 환경설정에서 기존 단축키를 해제한 후 사용하세요.
- `ToggleComponentVisibility`의 `V` 단축키는 기존 Body 숨기기 단축키를 **대체**합니다.
- 애드인은 Fusion 360 업데이트 후 재실행이 필요할 수 있습니다.

---

## 🔧 개발 환경

- Fusion 360 (최신 버전)
- Python 3.x (Fusion 360 내장)
- Windows 10/11

---

*Made with ❤️ to speed up Fusion 360 workflows*
