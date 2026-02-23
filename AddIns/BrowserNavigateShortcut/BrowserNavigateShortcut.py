import adsk.core, adsk.fusion, traceback
import ctypes
import time

_handlers = []
_app = None
_ui = None

# Windows API 상수
VK_RIGHT = 0x27
VK_DOWN = 0x28
KEYEVENTF_KEYUP = 0x0002

def run(context):
    global _app, _ui
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # 기존 명령어 정리
        oldCmd = _ui.commandDefinitions.itemById('BrowserNavigateShortcut')
        if oldCmd:
            oldCmd.deleteMe()

        # 새 명령어 생성
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'BrowserNavigateShortcut',
            '브라우저 탐색',
            '현재 컴포넌트를 선택하고 브라우저에서 화살표 키로 탐색합니다.'
        )

        # 명령어 실행 핸들러
        class ExecuteHandler(adsk.core.CommandEventHandler):
            def notify(self, args):
                try:
                    # 사용자가 이미 선택한 상태에서 시작
                    # 화살표 키만 전송
                    
                    # 오른쪽 (컴포넌트 확장)
                    self.send_key(VK_RIGHT)
                    time.sleep(0.1)
                    
                    # 아래 3번 (Bodies, Construction, Sketches로 이동)
                    self.send_key(VK_DOWN)
                    time.sleep(0.1)
                    
                    self.send_key(VK_DOWN)
                    time.sleep(0.1)
                    
                    self.send_key(VK_DOWN)
                    time.sleep(0.1)
                    
                    # 오른쪽 (Sketches 폴더 확장)
                    self.send_key(VK_RIGHT)
                    
                except Exception as e:
                    if _ui:
                        _ui.messageBox('에러:\n{}'.format(str(e)))
            
            def send_key(self, vk_code):
                """Windows SendInput API를 사용하여 키 입력 시뮬레이션 (더 안정적)"""
                try:
                    # SendInput 구조체 정의
                    PUL = ctypes.POINTER(ctypes.c_ulong)
                    
                    class KeyBdInput(ctypes.Structure):
                        _fields_ = [("wVk", ctypes.c_ushort),
                                    ("wScan", ctypes.c_ushort),
                                    ("dwFlags", ctypes.c_ulong),
                                    ("time", ctypes.c_ulong),
                                    ("dwExtraInfo", PUL)]
                    
                    class HardwareInput(ctypes.Structure):
                        _fields_ = [("uMsg", ctypes.c_ulong),
                                    ("wParamL", ctypes.c_short),
                                    ("wParamH", ctypes.c_ushort)]
                    
                    class MouseInput(ctypes.Structure):
                        _fields_ = [("dx", ctypes.c_long),
                                    ("dy", ctypes.c_long),
                                    ("mouseData", ctypes.c_ulong),
                                    ("dwFlags", ctypes.c_ulong),
                                    ("time", ctypes.c_ulong),
                                    ("dwExtraInfo", PUL)]
                    
                    class Input_I(ctypes.Union):
                        _fields_ = [("ki", KeyBdInput),
                                    ("mi", MouseInput),
                                    ("hi", HardwareInput)]
                    
                    class Input(ctypes.Structure):
                        _fields_ = [("type", ctypes.c_ulong),
                                    ("ii", Input_I)]
                    
                    # 키 누름
                    extra = ctypes.c_ulong(0)
                    ii_ = Input_I()
                    ii_.ki = KeyBdInput(vk_code, 0, 0, 0, ctypes.pointer(extra))
                    x = Input(ctypes.c_ulong(1), ii_)
                    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                    
                    time.sleep(0.02)
                    
                    # 키 뗌
                    ii_.ki = KeyBdInput(vk_code, 0, 0x0002, 0, ctypes.pointer(extra))  # KEYEVENTF_KEYUP = 0x0002
                    x = Input(ctypes.c_ulong(1), ii_)
                    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                    
                except Exception as e:
                    # SendInput 실패 시 기존 방법 시도
                    try:
                        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
                        time.sleep(0.01)
                        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
                    except:
                        pass

        # 명령어 생성 핸들러
        class CreatedHandler(adsk.core.CommandCreatedEventHandler):
            def notify(self, args):
                onExecute = ExecuteHandler()
                args.command.execute.add(onExecute)
                _handlers.append(onExecute)

        onCreated = CreatedHandler()
        cmdDef.commandCreated.add(onCreated)
        _handlers.append(onCreated)

        # 단축키 등록 시도 (Ctrl+Shift+N)
        shortcut_registered = False
        try:
            shortcut = _ui.keyboardShortcuts.add('BrowserNavigateShortcut', 'N', True, True, False)
            if shortcut:
                shortcut.bind(cmdDef)
                shortcut_registered = True
        except:
            pass

        # SOLID -> MODIFY 패널에 버튼 추가
        modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
        if modifyPanel:
            ctrl = modifyPanel.controls.itemById('BrowserNavigateShortcut')
            if ctrl:
                ctrl.deleteMe()
            modifyPanel.controls.addCommand(cmdDef)

        # 성공 메시지
        if shortcut_registered:
            _ui.messageBox('✅ 브라우저 탐색 애드인 로드 완료!\n\n단축키: Ctrl+Shift+N\n\n동작:\n→ ↓ ↓ ↓ →')
        else:
            _ui.messageBox('✅ 브라우저 탐색 애드인 로드 완료!\n\n📌 단축키 설정:\n파일 > 환경설정 > 단축키 > "브라우저 탐색" 검색\n\n동작:\n→ ↓ ↓ ↓ →')

    except Exception as e:
        if _ui:
            _ui.messageBox('로드 실패:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        if _ui:
            # 단축키 제거
            shortcut = _ui.keyboardShortcuts.itemById('BrowserNavigateShortcut')
            if shortcut:
                shortcut.deleteMe()
            
            # 명령어 삭제
            cmdDef = _ui.commandDefinitions.itemById('BrowserNavigateShortcut')
            if cmdDef:
                cmdDef.deleteMe()
            
            # 패널에서 버튼 제거
            modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
            if modifyPanel:
                ctrl = modifyPanel.controls.itemById('BrowserNavigateShortcut')
                if ctrl:
                    ctrl.deleteMe()
    except:
        pass
