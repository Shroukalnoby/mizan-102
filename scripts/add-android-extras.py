"""Adds the Mizan home-screen widget and the mizan://add link to the generated Android project.
Runs in the cloud build right after `npx cap add android`. Safe to run twice."""
import os, re, sys

APP = 'android/app/src/main'
PKG = 'app.mizan.budget'
JAVA = os.path.join(APP, 'java', *PKG.split('.'))
RES = os.path.join(APP, 'res')
if not os.path.isdir(APP):
    sys.exit('android project not found - run "npx cap add android" first')

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

write(os.path.join(JAVA, 'MainActivity.java'), '''package app.mizan.budget;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(MizanWidgetPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
''')

write(os.path.join(JAVA, 'MizanWidgetPlugin.java'), '''package app.mizan.budget;

import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "MizanWidget")
public class MizanWidgetPlugin extends Plugin {
    @PluginMethod
    public void refresh(PluginCall call) {
        Context c = getContext();
        AppWidgetManager m = AppWidgetManager.getInstance(c);
        int[] ids = m.getAppWidgetIds(new ComponentName(c, MizanWidget.class));
        for (int id : ids) {
            MizanWidget.update(c, m, id);
        }
        call.resolve();
    }
}
''')

write(os.path.join(JAVA, 'MizanWidget.java'), '''package app.mizan.budget;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.view.View;
import android.widget.RemoteViews;
import org.json.JSONObject;

public class MizanWidget extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) {
            update(context, manager, id);
        }
    }

    static void update(Context context, AppWidgetManager manager, int id) {
        RemoteViews v = new RemoteViews(context.getPackageName(), R.layout.mizan_widget);
        String title = "Mizan";
        String month = "";
        String balance = "";
        String line = "";
        String locked = "Open Mizan";
        int pct = 0;
        boolean pro = false;
        try {
            String raw = context.getSharedPreferences("CapacitorStorage", Context.MODE_PRIVATE).getString("mizan_widget", null);
            if (raw != null) {
                JSONObject o = new JSONObject(raw);
                pro = o.optBoolean("pro", false);
                title = o.optString("title", title);
                month = o.optString("month", "");
                balance = o.optString("balance", "");
                line = o.optString("line", "");
                locked = o.optString("locked", locked);
                pct = o.optInt("pct", 0);
            }
        } catch (Exception e) {
            // show the placeholder text
        }

        v.setTextViewText(R.id.w_title, title);
        if (pro) {
            v.setTextViewText(R.id.w_month, month);
            v.setTextViewText(R.id.w_balance, balance);
            v.setTextViewText(R.id.w_line, line);
            v.setProgressBar(R.id.w_bar, 100, pct, false);
            v.setViewVisibility(R.id.w_bar, View.VISIBLE);
        } else {
            v.setTextViewText(R.id.w_month, "");
            v.setTextViewText(R.id.w_balance, "");
            v.setTextViewText(R.id.w_line, locked);
            v.setViewVisibility(R.id.w_bar, View.GONE);
        }

        int flags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE;
        Intent open = new Intent(context, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        v.setOnClickPendingIntent(R.id.w_root, PendingIntent.getActivity(context, 0, open, flags));

        Intent add = new Intent(Intent.ACTION_VIEW, Uri.parse("mizan://add"), context, MainActivity.class);
        add.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        v.setOnClickPendingIntent(R.id.w_add, PendingIntent.getActivity(context, 1, add, flags));

        manager.updateAppWidget(id, v);
    }
}
''')

write(os.path.join(RES, 'layout', 'mizan_widget.xml'), '''<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/w_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/mizan_widget_bg"
    android:padding="14dp">

    <TextView
        android:id="@+id/w_title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignParentStart="true"
        android:text="Mizan"
        android:textColor="#1E6B5A"
        android:textSize="13sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/w_month"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_toEndOf="@id/w_title"
        android:layout_marginStart="8dp"
        android:textColor="#566860"
        android:textSize="12sp" />

    <TextView
        android:id="@+id/w_add"
        android:layout_width="36dp"
        android:layout_height="36dp"
        android:layout_alignParentEnd="true"
        android:background="@drawable/mizan_widget_btn"
        android:gravity="center"
        android:text="+"
        android:textColor="#FFFFFF"
        android:textSize="22sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/w_balance"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_below="@id/w_title"
        android:layout_marginTop="6dp"
        android:layout_marginEnd="44dp"
        android:maxLines="1"
        android:textColor="#14221D"
        android:textSize="24sp"
        android:textStyle="bold" />

    <ProgressBar
        android:id="@+id/w_bar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="6dp"
        android:layout_below="@id/w_balance"
        android:layout_marginTop="6dp"
        android:max="100"
        android:progress="0"
        android:progressTint="#1E6B5A" />

    <TextView
        android:id="@+id/w_line"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_below="@id/w_bar"
        android:layout_marginTop="6dp"
        android:maxLines="2"
        android:textColor="#566860"
        android:textSize="12sp" />
</RelativeLayout>
''')

write(os.path.join(RES, 'drawable', 'mizan_widget_bg.xml'), '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#F7FBF8" />
    <corners android:radius="22dp" />
    <stroke android:width="1dp" android:color="#D5DFD9" />
</shape>
''')
write(os.path.join(RES, 'drawable', 'mizan_widget_btn.xml'), '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#1E6B5A" />
</shape>
''')
write(os.path.join(RES, 'xml', 'mizan_widget_info.xml'), '''<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp"
    android:minHeight="110dp"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/mizan_widget"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen" />
''')

# ---- manifest: widget receiver, mizan://add link, notification permission
mf = os.path.join(APP, 'AndroidManifest.xml')
m = open(mf, encoding='utf-8').read()
if 'MizanWidget' not in m:
    receiver = '''
        <receiver android:name=".MizanWidget" android:exported="true">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/mizan_widget_info" />
        </receiver>
'''
    assert '</application>' in m
    m = m.replace('</application>', receiver + '    </application>', 1)
    link = '''            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="mizan" android:host="add" />
            </intent-filter>
'''
    mm = re.search(r'<activity\b[^>]*MainActivity[^>]*>.*?</activity>', m, re.S)
    assert mm, 'MainActivity block not found'
    block = mm.group(0)
    m = m.replace(block, block.replace('</activity>', link + '        </activity>'), 1)
if 'POST_NOTIFICATIONS' not in m:
    m = m.replace('</manifest>', '    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n</manifest>', 1)
open(mf, 'w', encoding='utf-8').write(m)
print('Mizan widget + link added')
