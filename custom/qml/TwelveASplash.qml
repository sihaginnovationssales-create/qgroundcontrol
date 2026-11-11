import QtQuick
import QtQuick.Window

// Startup animation laid over the main window by CustomPlugin::createRootWindow(). It continues
// the Android launch screen (android/res/drawable/splashscreen.xml: @drawable/icon centered on
// black): the badge starts at that size, zooms up, then the overlay fades out. Tap to skip.
Rectangle {
    id: root

    // Android draws the 144 px launcher bitmap at 48 dp (36 dp on xxxhdpi screens) and the badge
    // fills 96 % of it. Logical pixels equal dp on Android.
    readonly property real _startHeight:    (Screen.devicePixelRatio > 3 ? 36 : 48) * 0.96
    readonly property real _endHeight:      Math.min(width, height) * 0.5

    function _hide() {
        visible = false
        badge.source = ""   // release the large texture
    }

    anchors.fill:   parent
    z:              1000000
    color:          "#000000"   // same black as the Android launch screen, not a theme color

    Image {
        id:                 badge
        anchors.centerIn:   parent
        height:             root._endHeight
        width:              height * sourceSize.width / Math.max(1, sourceSize.height)
        scale:              root._startHeight / Math.max(1, root._endHeight)
        source:             "qrc:/Custom/res/SplashBadge.png"
        fillMode:           Image.PreserveAspectFit
        smooth:             true
        mipmap:             true
    }

    MouseArea {
        anchors.fill:   parent
        onClicked: {
            intro.stop()
            root._hide()
        }
    }

    SequentialAnimation {
        id:         intro
        running:    true

        PauseAnimation  { duration: 150 }
        NumberAnimation { target: badge; property: "scale"; to: 1; duration: 900; easing.type: Easing.OutBack }
        PauseAnimation  { duration: 450 }
        NumberAnimation { target: root; property: "opacity"; to: 0; duration: 400; easing.type: Easing.InQuad }
        ScriptAction    { script: root._hide() }
    }
}
