import QtQuick
import QtQuick.Window

import QGroundControl
import QGroundControl.Controls

// 12 Armoured override of src/FlyView/FlyViewCustomLayer.qml, the Fly view's customization layer.
// While no vehicle is connected it covers the map and flight widgets (below the toolbar) with the
// 12 ARMOURED branding and a connection-status button in the exact centre of the screen. When a
// vehicle connects it hides, so the map and every flight widget are back unchanged.
Item {
    id: _root

    // Interface FlyView.qml sets on this layer (same as upstream)
    property var occluders
    property var customOccluders: []
    property var mapControl

    // Brand colors from the 12 Armoured crest, deliberately fixed rather than theme colors
    readonly property color _brandBackground:   "#121212"
    readonly property color _brandCharcoal:     "#1C1C1C"
    readonly property color _brandGold:         "#E7B321"
    readonly property color _brandMuted:        "#9C8440"

    readonly property bool _vehicleConnected:   !!QGroundControl.multiVehicleManager.activeVehicle
    // FlyView insets this layer from the window by the toolbar height plus this widget margin
    readonly property real _widgetMargin:       ScreenTools.defaultFontPixelWidth * 0.75
    readonly property real _topInWindow:        ScreenTools.toolbarHeight + _widgetMargin
    readonly property real _windowCentreY:      (Window.height / 2) - _topInWindow
    readonly property real _spacing:            ScreenTools.defaultFontPixelHeight

    Rectangle {
        id:                     brandScreen
        objectName:             "twelveArmouredBrandScreen"
        anchors.fill:           parent
        anchors.margins:        -_root._widgetMargin
        color:                  _root._brandBackground
        visible:                !_root._vehicleConnected

        // Swallow input so the hidden map and widgets underneath can't be operated
        MouseArea {
            anchors.fill:       parent
            acceptedButtons:    Qt.AllButtons
            onWheel:            (wheel) => { wheel.accepted = true }
        }

        // Badge with the name beside it, centred in the space between the toolbar and the status
        // button. Side by side because a landscape phone has little height above the centre.
        Item {
            id:                     brandArea
            anchors.left:           parent.left
            anchors.right:          parent.right
            anchors.top:            parent.top
            anchors.bottom:         statusButton.top
            anchors.margins:        _root._spacing * 0.5

            Row {
                id:                 brandRow
                anchors.centerIn:   parent
                spacing:            _root._spacing

                Image {
                    id:         brandLogo
                    height:     Math.min(brandArea.height, ScreenTools.defaultFontPixelHeight * 14)
                    width:      height * sourceSize.width / Math.max(1, sourceSize.height)
                    source:     "qrc:/Custom/res/SplashBadge.png"
                    fillMode:   Image.PreserveAspectFit
                    smooth:     true
                    mipmap:     true
                }

                // Shrinks to fit beside the crest on narrow screens instead of running off the edge
                QGCLabel {
                    anchors.verticalCenter: parent.verticalCenter
                    width:                  Math.min(implicitWidth,
                                                     brandArea.width - brandLogo.width - brandRow.spacing)
                    text:                   qsTr("12 ARMOURED REGIMENT")
                    color:                  _root._brandGold
                    font.pointSize:         ScreenTools.largeFontPointSize * 1.9
                    font.bold:              true
                    font.letterSpacing:     ScreenTools.defaultFontPixelWidth * 0.4
                    fontSizeMode:           Text.HorizontalFit
                    minimumPointSize:       ScreenTools.mediumFontPointSize
                    elide:                  Text.ElideNone
                }
            }
        }

        // Below the centred button, mirroring the branding above so the screen stays balanced
        Item {
            id:                     captionArea
            anchors.left:           parent.left
            anchors.right:          parent.right
            anchors.top:            statusButton.bottom
            anchors.bottom:         parent.bottom

            QGCLabel {
                anchors.centerIn:   parent
                text:               qsTr("GROUND CONTROL STATION")
                color:              _root._brandMuted
                font.pointSize:     ScreenTools.largeFontPointSize
                font.letterSpacing: ScreenTools.defaultFontPixelWidth * 0.6
            }
        }

        // Connection status, centred on the window (not on this layer, which starts below the toolbar)
        Rectangle {
            id:                         statusButton
            objectName:                 "twelveArmouredConnectButton"
            anchors.horizontalCenter:   parent.horizontalCenter
            y:                          _root._windowCentreY + _root._widgetMargin - (height / 2)
            width:                      statusLabel.contentWidth + ScreenTools.defaultFontPixelWidth * 4
            height:                     statusLabel.contentHeight + ScreenTools.defaultFontPixelHeight
            radius:                     height / 2
            color:                      statusMouseArea.pressed ? Qt.lighter(_root._brandCharcoal, 1.6)
                                                                : _root._brandCharcoal
            border.color:               _root._brandGold
            border.width:               Math.max(2, ScreenTools.defaultFontPixelWidth * 0.2)

            QGCLabel {
                id:                 statusLabel
                anchors.centerIn:   parent
                text:               qsTr("DISCONNECTED – CLICK TO MANUALLY CONNECT")
                color:              _root._brandGold
                font.pointSize:     ScreenTools.largeFontPointSize
                font.bold:          true
            }

            QGCMouseArea {
                id:             statusMouseArea
                anchors.fill:   parent
                onClicked:      flyView.dropMainStatusIndicatorTool()
            }
        }
    }
}
