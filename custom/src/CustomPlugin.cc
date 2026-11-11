#include "CustomPlugin.h"
#include "QGCLoggingCategory.h"

#include <QtCore/QApplicationStatic>
#include <QtCore/QFile>
#include <QtGui/QGuiApplication>
#include <QtQml/QQmlApplicationEngine>
#include <QtQml/QQmlComponent>
#include <QtQuick/QQuickItem>
#include <QtQuick/QQuickWindow>

QGC_LOGGING_CATEGORY(CustomLog, "Custom.CustomPlugin")

Q_APPLICATION_STATIC(CustomPlugin, _customPluginInstance);

CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
{
    qCDebug(CustomLog) << this;

    // On-screen name ("12 Armoured"). applicationName() stays the safe identifier
    // (TwelveArmoured) because it also names settings/save folders and the network
    // User-Agent. Window titles and QGroundControl.appName use this display name.
    QGuiApplication::setApplicationDisplayName(QStringLiteral(TWELVEA_DISPLAY_NAME));
}

QGCCorePlugin *CustomPlugin::instance()
{
    return _customPluginInstance();
}

QQmlApplicationEngine *CustomPlugin::createQmlApplicationEngine(QObject *parent)
{
    _qmlEngine = QGCCorePlugin::createQmlApplicationEngine(parent);

    _urlInterceptor = new CustomOverrideInterceptor();
    _qmlEngine->addUrlInterceptor(_urlInterceptor);

    return _qmlEngine;
}

void CustomPlugin::destroyQmlApplicationEngine(QQmlApplicationEngine *qmlEngine)
{
    if (qmlEngine && (qmlEngine == _qmlEngine)) {
        qmlEngine->removeUrlInterceptor(_urlInterceptor);
        delete _urlInterceptor;
        _urlInterceptor = nullptr;
        _qmlEngine = nullptr;
    }

    QGCCorePlugin::destroyQmlApplicationEngine(qmlEngine);
}

void CustomPlugin::createRootWindow(QQmlApplicationEngine *qmlEngine)
{
    QGCCorePlugin::createRootWindow(qmlEngine);

    const QList<QObject*> rootObjects = qmlEngine->rootObjects();
    QQuickWindow *const window =
        rootObjects.isEmpty() ? nullptr : qobject_cast<QQuickWindow*>(rootObjects.constFirst());
    if (!window) {
        qCWarning(CustomLog) << "No root window, skipping startup animation";
        return;
    }

    // beginCreate/completeCreate so the overlay has its parent before its bindings first run.
    QQmlComponent component(qmlEngine, QUrl(QStringLiteral("qrc:/Custom/qml/TwelveASplash.qml")));
    QObject *const object = component.beginCreate(qmlEngine->rootContext());
    QQuickItem *const splash = qobject_cast<QQuickItem*>(object);
    if (!splash) {
        qCWarning(CustomLog) << "Startup animation failed to load:" << component.errors();
        delete object;
        return;
    }

    splash->setParent(window->contentItem());
    splash->setParentItem(window->contentItem());
    component.completeCreate();
}

/*===========================================================================*/

CustomOverrideInterceptor::CustomOverrideInterceptor()
    : QQmlAbstractUrlInterceptor()
{

}

QUrl CustomOverrideInterceptor::intercept(const QUrl &url, QQmlAbstractUrlInterceptor::DataType type)
{
    switch (type) {
    case QQmlAbstractUrlInterceptor::QmlFile:
    case QQmlAbstractUrlInterceptor::UrlString:
        if (url.scheme() == QStringLiteral("qrc")) {
            const QString origPath = url.path();
            const QString overrideRes = QStringLiteral(":/Custom%1").arg(origPath);
            if (QFile::exists(overrideRes)) {
                const QString relPath = overrideRes.mid(2);
                QUrl result;
                result.setScheme(QStringLiteral("qrc"));
                result.setPath('/' + relPath);
                return result;
            }
        }
        break;
    default:
        break;
    }

    return url;
}
