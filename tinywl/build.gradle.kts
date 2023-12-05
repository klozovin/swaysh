plugins {
    java
    application
    kotlin("jvm") version "1.9.21"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(platform(kotlin("bom")))
    implementation(kotlin("stdlib"))
}

tasks.withType<JavaCompile> {
    options.compilerArgs.addAll(listOf(
        "--enable-preview"
    ))
}
application {
    mainClass.set("tinywl.TinyWL")

    applicationDefaultJvmArgs = listOf(
        "--enable-preview",
        "--enable-native-access", "ALL-UNNAMED",
        "-Dforeign.restricted=permit",
    )
}
