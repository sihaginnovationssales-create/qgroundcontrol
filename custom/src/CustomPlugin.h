#pragma once

// 12 Armoured custom plugin: branding only.
// Derived from custom-example/src/CustomPlugin.h with the demo features removed.

#include <QtCore/QLoggingCategory>
#include <QtQml/QQmlAbstractUrlInterceptor>

#include "QGCCorePlugin.h"

class QQmlApplicationEngine;
class CustomOverrideInterceptor;

Q_DECLARE_LOGGING_CATEGORY(CustomLog)

class CustomPlugin : public QGCCorePlugin
{
    Q_OBJECT

public:
    explicit CustomPlugin(QObject *parent = nullptr);

    static QGCCorePlugin *instance();

    // Overrides from QGCCorePlugin

    /// Installs the URL interceptor that serves the 12 Armoured logos in place of the stock ones.
    QQmlApplicationEngine *createQmlApplicationEngine(QObject *parent) final;
    /// Releases the url interceptor attached in createQmlApplicationEngine before the engine is destroyed.
    void destroyQmlApplicationEngine(QQmlApplicationEngine *qmlEngine) final;
    /// Loads the main window, then lays the startup zoom animation (TwelveASplash.qml) over it.
    void createRootWindow(QQmlApplicationEngine *qmlEngine) final;
    /// Where the "Update" link points. The version check itself is already off for custom builds.
    QString stableDownloadUrl() const final { return QStringLiteral(TWELVEA_DOWNLOAD_URL); }

private:
    QQmlApplicationEngine *_qmlEngine = nullptr;
    CustomOverrideInterceptor *_urlInterceptor = nullptr;
};

/*===========================================================================*/

/// Redirects qrc:/<path> to qrc:/Custom/<path> when an override resource exists.
class CustomOverrideInterceptor : public QQmlAbstractUrlInterceptor
{
public:
    CustomOverrideInterceptor();

    QUrl intercept(const QUrl &url, QQmlAbstractUrlInterceptor::DataType type) final;
};
