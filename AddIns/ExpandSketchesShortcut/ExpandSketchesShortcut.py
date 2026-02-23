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
        oldCmd = _ui.commandDefinitions.itemById('ExpandSketchesShortcut')
        if oldCmd:
            oldCmd.deleteMe()

        # 새 명령어 생성
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'ExpandSketchesShortcut',
            'Sketches 폴더 열기',
            '현재 활성 컴포넌트의 Sketches 폴더를 브라우저에서 확장합니다.'
        )

        # 명령어 실행 핸들러
        class ExecuteHandler(adsk.core.CommandEventHandler):
            def notify(self, args):
                try:
                    design = adsk.fusion.Design.cast(_app.activeProduct)
                    if not design:
                        return

                    # 현재 활성 컴포넌트의 첫 번째 스케치 선택
                    # 이렇게 하면 브라우저에서 Sketches 폴더가 자동으로 확장됨
                    active_comp = design.activeComponent
                    
                    if active_comp.sketches.count > 0:
                        # 첫 번째 스케치 선택
                        first_sketch = active_comp.sketches.item(0)
                        _ui.activeSelections.clear()
                        _ui.activeSelections.add(first_sketch)
                    else:
                        # 스케치가 없으면 메시지 표시
                        _ui.messageBox('현재 컴포넌트에 스케치가 없습니다.')
                    
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

        # 단축키 등록 시도 (Ctrl+Shift+S)
        shortcut_registered = False
        try:
            shortcut = _ui.keyboardShortcuts.add('ExpandSketchesShortcut', 'S', True, True, False)
            if shortcut:
                shortcut.bind(cmdDef)
                shortcut_registered = True
        except:
            pass

        # SOLID -> MODIFY 패널에 버튼 추가
        modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
        if modifyPanel:
            ctrl = modifyPanel.controls.itemById('ExpandSketchesShortcut')
            if ctrl:
                ctrl.deleteMe()
            modifyPanel.controls.addCommand(cmdDef)

        # 성공 메시지
        if shortcut_registered:
            _ui.messageBox('✅ Sketches 폴더 열기 애드인 로드 완료!\n\n단축키: Ctrl+Shift+S\n\n현재 컴포넌트의 첫 번째 스케치를 선택하여\nSketches 폴더를 자동으로 확장합니다.')
        else:
            _ui.messageBox('✅ Sketches 폴더 열기 애드인 로드 완료!\n\n📌 단축키 설정:\n파일 > 환경설정 > 단축키 > "Sketches 폴더 열기" 검색')

    except Exception as e:
        if _ui:
            _ui.messageBox('로드 실패:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        if _ui:
            # 단축키 제거
            shortcut = _ui.keyboardShortcuts.itemById('ExpandSketchesShortcut')
            if shortcut:
                shortcut.deleteMe()
            
            # 명령어 삭제
            cmdDef = _ui.commandDefinitions.itemById('ExpandSketchesShortcut')
            if cmdDef:
                cmdDef.deleteMe()
            
            # 패널에서 버튼 제거
            modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
            if modifyPanel:
                ctrl = modifyPanel.controls.itemById('ExpandSketchesShortcut')
                if ctrl:
                    ctrl.deleteMe()
    except:
        pass
