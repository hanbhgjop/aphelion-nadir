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
        oldCmd = _ui.commandDefinitions.itemById('SelectActiveComponent')
        if oldCmd:
            oldCmd.deleteMe()

        # 새 명령어 생성
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'SelectActiveComponent',
            '활성 컴포넌트 선택',
            '현재 활성화된 컴포넌트를 브라우저에서 선택합니다.'
        )

        # 명령어 실행 핸들러
        class ExecuteHandler(adsk.core.CommandEventHandler):
            def notify(self, args):
                try:
                    design = adsk.fusion.Design.cast(_app.activeProduct)
                    if not design:
                        return

                    active_comp = design.activeComponent
                    
                    # Root component인 경우 직접 선택 가능
                    if active_comp == design.rootComponent:
                        _ui.activeSelections.clear()
                        _ui.activeSelections.add(active_comp)
                    else:
                        # 하위 컴포넌트인 경우 해당 occurrence를 찾아서 선택
                        # Root에서 재귀적으로 탐색
                        occ = self.find_occurrence(design.rootComponent, active_comp)
                        
                        if occ:
                            _ui.activeSelections.clear()
                            _ui.activeSelections.add(occ)
                        else:
                            _ui.messageBox('활성 컴포넌트의 occurrence를 찾을 수 없습니다.')
                    
                except Exception as e:
                    if _ui:
                        _ui.messageBox('에러:\n{}'.format(str(e)))
            
            def find_occurrence(self, parent_comp, target_comp):
                """재귀적으로 target_comp의 occurrence 찾기"""
                # 직접 자식 확인
                for occ in parent_comp.occurrences:
                    if occ.component == target_comp:
                        return occ
                    
                    # 재귀적으로 하위 탐색
                    found = self.find_occurrence(occ.component, target_comp)
                    if found:
                        return found
                
                return None

        # 명령어 생성 핸들러
        class CreatedHandler(adsk.core.CommandCreatedEventHandler):
            def notify(self, args):
                onExecute = ExecuteHandler()
                args.command.execute.add(onExecute)
                _handlers.append(onExecute)

        onCreated = CreatedHandler()
        cmdDef.commandCreated.add(onCreated)
        _handlers.append(onCreated)

        # 단축키 등록 시도 (Ctrl+Shift+A)
        shortcut_registered = False
        try:
            shortcut = _ui.keyboardShortcuts.add('SelectActiveComponent', 'A', True, True, False)
            if shortcut:
                shortcut.bind(cmdDef)
                shortcut_registered = True
        except:
            pass

        # SOLID -> MODIFY 패널에 버튼 추가
        modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
        if modifyPanel:
            ctrl = modifyPanel.controls.itemById('SelectActiveComponent')
            if ctrl:
                ctrl.deleteMe()
            modifyPanel.controls.addCommand(cmdDef)

        # 성공 메시지
        if shortcut_registered:
            _ui.messageBox('✅ 활성 컴포넌트 선택 애드인 로드 완료!\n\n단축키: Ctrl+Shift+A\n\n현재 활성화된 컴포넌트를 브라우저에서 선택합니다.')
        else:
            _ui.messageBox('✅ 활성 컴포넌트 선택 애드인 로드 완료!\n\n📌 단축키 설정:\n파일 > 환경설정 > 단축키 > "활성 컴포넌트 선택" 검색')

    except Exception as e:
        if _ui:
            _ui.messageBox('로드 실패:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        if _ui:
            # 단축키 제거
            shortcut = _ui.keyboardShortcuts.itemById('SelectActiveComponent')
            if shortcut:
                shortcut.deleteMe()
            
            # 명령어 삭제
            cmdDef = _ui.commandDefinitions.itemById('SelectActiveComponent')
            if cmdDef:
                cmdDef.deleteMe()
            
            # 패널에서 버튼 제거
            modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
            if modifyPanel:
                ctrl = modifyPanel.controls.itemById('SelectActiveComponent')
                if ctrl:
                    ctrl.deleteMe()
    except:
        pass
