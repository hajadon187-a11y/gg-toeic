import java.time.Duration

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp")
    id("com.google.dagger.hilt.android")
    id("org.jetbrains.kotlin.plugin.compose")
}


android {
    namespace = "com.gachiguild.gachitoefl"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.gachiguild.gachitoefl"
        minSdk = 29
        targetSdk = 36
        versionCode = 2
        versionName = "1.0"
        buildConfigField("boolean", "PRODUCTION_MODE", "false")
    }

    buildTypes {
        getByName("debug") {
            // 通常のデバッグAPKではTOEFL 100+を無条件で確認できるようにする。
            buildConfigField("boolean", "PRODUCTION_MODE", "false")
        }
        getByName("release") {
            buildConfigField("boolean", "PRODUCTION_MODE", "true")
        }
        create("productionDebug") {
            // デバッガ接続は許可しつつ、課金・通知だけ本番挙動にする。
            initWith(getByName("debug"))
            isDebuggable = true
            buildConfigField("boolean", "PRODUCTION_MODE", "true")
            matchingFallbacks += listOf("debug")
        }
    }


    buildFeatures {
        compose = true
        buildConfig = true
    }

    testOptions {
        unitTests {
            isReturnDefaultValues = true
        }
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

tasks.withType<Test>().configureEach {
    // ハング防止のためタイムアウトを設定（5分で強制終了）
    timeout = Duration.ofMinutes(5)

    testLogging {
        // 進捗が見えるようにテストの標準出力をライブ表示する
        events("started", "passed", "failed", "skipped")
        showStandardStreams = true
        showExceptions = true
        showStackTraces = true
        showCauses = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.core:core-splashscreen:1.0.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.4")
    implementation("androidx.activity:activity-compose:1.2.9")
    implementation(platform("androidx.compose:compose-bom:2024.10.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.room:room-runtime:2.7.1")
    implementation("androidx.room:room-ktx:2.7.1")
    ksp("androidx.room:room-compiler:2.7.1")

    implementation("com.google.dagger:hilt-android:2.56.2")
    ksp("com.google.dagger:hilt-compiler:2.56.2")
    implementation("androidx.hilt:hilt-navigation-compose:1.0.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.4")
    implementation("com.android.billingclient:billing-ktx:8.0.0")

    testImplementation("junit:junit:4.13.2")
    testImplementation("androidx.room:room-testing:2.7.1")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
    testImplementation("org.robolectric:robolectric:4.12.2")
    testImplementation("androidx.test:core:1.6.1")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2024.10.00"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
