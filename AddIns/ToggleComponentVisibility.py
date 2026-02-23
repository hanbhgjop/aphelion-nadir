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
        oldCmd = _ui.commandDefinitions.itemById('ToggleComponentVisibility')
        if oldCmd:
            oldCmd.deleteMe()

        # 새 명령어 생성
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'ToggleComponentVisibility',
            '컴포넌트 숨기기/보이기',
            '선택한 본체의 상위 컴포넌트를 숨기거나 보이게 합니다.'
        )

        # 명령어 실행 핸들러
        class ExecuteHandler(adsk.core.CommandEventHandler):
            def notify(self, args):
                try:
                    design = adsk.fusion.Design.cast(_app.activeProduct)
                    if not design:
                        return

                    # 현재 선택된 항목 가져오기
                    selections = _ui.activeSelections
                    if selections.count == 0:
                        return
                    
                    # 첫 번째 선택 항목
                    selected_entity = selections.item(0).entity
                    
                    # 선택된 항목 처리
                    target_occ = None
                    
                    # 이미 Occurrence를 선택한 경우
                    if isinstance(selected_entity, adsk.fusion.Occurrence):
                        target_occ = selected_entity
                    else:
                        # 선택된 항목의 컴포넌트 찾기
                        component = None
                        
                        # BRepBody, BRepFace, BRepEdge 등 parentComponent 속성이 있는 경우
                        try:
                            if hasattr(selected_entity, 'body') and selected_entity.body:
                                # Face, Edge 등은 body를 통해 접근
                                component = selected_entity.body.parentComponent
                            elif hasattr(selected_entity, 'parentComponent'):
                                # Body는 직접 parentComponent 접근
                                component = selected_entity.parentComponent
                        except:
                            pass
                        
                        # Component인 경우
                        if not component and isinstance(selected_entity, adsk.fusion.Component):
                            component = selected_entity
                        
                        if not component:
                            return
                        
                        # Root component인 경우
                        if component == design.rootComponent:
                            return
                        
                        # 컴포넌트의 occurrence 찾기
                        target_occ = self.find_occurrence(design.rootComponent, component)
                        
                        if not target_occ:
                            return
                    
                    # Occurrence 선택 및 visibility 토글
                    _ui.activeSelections.clear()
                    _ui.activeSelections.add(target_occ)
                    
                    # Visibility 토글
                    target_occ.isLightBulbOn = not target_occ.isLightBulbOn
                    
                except:
                    # 에러 발생 시 조용히 무시
                    pass
            
            def find_occurrence(self, parent_comp, target_comp):
                """재귀적으로 target_comp의 occurrence 찾기"""
                for occ in parent_comp.occurrences:
                    if occ.component == target_comp:
                        return occ
                    
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

        # 단축키 등록 시도 (V)
        shortcut_registered = False
        try:
            # 기존 V 키 단축키 제거 시도
            old_shortcut = _ui.keyboardShortcuts.itemById('ToggleComponentVisibility')
            if old_shortcut:
                old_shortcut.deleteMe()
            
            shortcut = _ui.keyboardShortcuts.add('ToggleComponentVisibility', 'V', False, False, False)
            if shortcut:
                shortcut.bind(cmdDef)
                shortcut_registered = True
        except:
            pass

        # SOLID -> MODIFY 패널에 버튼 추가
        modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
        if modifyPanel:
            ctrl = modifyPanel.controls.itemById('ToggleComponentVisibility')
            if ctrl:
                ctrl.deleteMe()
            modifyPanel.controls.addCommand(cmdDef)

    except:
        # 로드 실패 시에도 조용히 무시
        pass

def stop(context):
    try:
        if _ui:
            # 단축키 제거
            shortcut = _ui.keyboardShortcuts.itemById('ToggleComponentVisibility')
            if shortcut:
                shortcut.deleteMe()
            
            # 명령어 삭제
            cmdDef = _ui.commandDefinitions.itemById('ToggleComponentVisibility')
            if cmdDef:
                cmdDef.deleteMe()
            
            # 패널에서 버튼 제거
            modifyPanel = _ui.allToolbarPanels.itemById('SolidModifyPanel')
            if modifyPanel:
                ctrl = modifyPanel.controls.itemById('ToggleComponentVisibility')
                if ctrl:
                    ctrl.deleteMe()
    except:
        pass
