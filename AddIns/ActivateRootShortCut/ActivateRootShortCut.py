import adsk.core, adsk.fusion, traceback

_handlers = []
_app = None
_ui = None

def run(context):
    global _app, _ui
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # 기존 명령어 정리
        oldCmd = _ui.commandDefinitions.itemById('SelectRootComponent')
        if oldCmd:
            oldCmd.deleteMe()

        # 새 명령어 생성
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'SelectRootComponent',
            '최상위 선택',
            '최상위 컴포넌트를 선택합니다. (선택 후 X를 눌러 활성화하세요)'
        )

        # 명령어 실행 핸들러
        class ExecuteHandler(adsk.core.CommandEventHandler):
            def notify(self, args):
                try:
                    design = adsk.fusion.Design.cast(_app.activeProduct)
                    if not design:
                        return

                    # 최상위 컴포넌트 선택
                    _ui.activeSelections.clear()
                    _ui.activeSelections.add(design.rootComponent)
                    
                except Exception as e:
                    if _ui:
                        _ui.messageBox('에러:\n{}'.format(str(e)))

        # 명령어 생성 핸들러
        class CreatedHandler(adsk.core.CommandCreatedEventHandler):
            def notify(self, args):
                onExecute = ExecuteHandler()
                args.command.execute.add(onExecute)
                _handlers.append(onExecute)

        onCreated = CreatedHandler()
        cmdDef.commandCreated.add(onCreated)
        _handlers.append(onCreated)

        # 단축키 등록 시도 (Shift+X)
        shortcut_registered = False
        try:
            shortcut = _ui.keyboardShortcuts.add('SelectRootComponent', 'X', True, False, False)
            if shortcut:
                shortcut.bind(cmdDef)
                shortcut_registered = True
        except:
            pass

        # SOLID -> MODIFY 패널에 버튼 추가
        modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
        if modifyPanel:
            ctrl = modifyPanel.controls.itemById('SelectRootComponent')
            if ctrl:
                ctrl.deleteMe()
            modifyPanel.controls.addCommand(cmdDef)

        # 성공 메시지
        if shortcut_registered:
            _ui.messageBox('✅ 최상위 선택 애드인 로드 완료!\n\n단축키: Shift+X\n\n사용법:\n1. Shift+X로 최상위 선택\n2. X를 눌러 활성화')
        else:
            _ui.messageBox('✅ 최상위 선택 애드인 로드 완료!\n\n📌 단축키 설정:\n파일 > 환경설정 > 단축키 > "최상위 선택" 검색\n\n사용법:\n1. 단축키로 최상위 선택\n2. X를 눌러 활성화')

    except Exception as e:
        if _ui:
            _ui.messageBox('로드 실패:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        if _ui:
            # 단축키 제거
            shortcut = _ui.keyboardShortcuts.itemById('SelectRootComponent')
            if shortcut:
                shortcut.deleteMe()
            
            # 명령어 삭제
            cmdDef = _ui.commandDefinitions.itemById('SelectRootComponent')
            if cmdDef:
                cmdDef.deleteMe()
            
            # 패널에서 버튼 제거
            modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
            if modifyPanel:
                ctrl = modifyPanel.controls.itemById('SelectRootComponent')
                if ctrl:
                    ctrl.deleteMe()
    except:
        pass