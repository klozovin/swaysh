buildDir = file(".gradle-build")

plugins {
    java
    application
}

repositories {
    mavenCentral()
}

tasks.withType<JavaCompile> {
    options.compilerArgs.addAll(listOf("--add-modules", "jdk.incubator.foreign"))
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

application {
    mainClass.set("tinyjwl.Tiny")

    applicationDefaultJvmArgs = listOf(
        "--enable-native-access", "ALL-UNNAMED",
        "--add-modules", "jdk.incubator.foreign",
        "-Dforeign.restricted=permit",
    )
}