import com.diffplug.spotless.kotlin.KtfmtStep.TrailingCommaManagementStrategy
import com.github.benmanes.gradle.versions.updates.DependencyUpdatesTask
import com.github.benmanes.gradle.versions.updates.resolutionstrategy.ComponentSelectionWithCurrent

plugins {
  application
  alias(libs.plugins.shadow)
  alias(libs.plugins.spotless)
  alias(libs.plugins.versions)
}

group = "duckpond.buriedincode"

version = "2026.2.0"

repositories {
  mavenLocal()
  mavenCentral()
}

dependencies {
  implementation(libs.gson)
  implementation(libs.jspecify)
  implementation(libs.playwright)
}

tasks.withType<JavaCompile>().configureEach {
  options.release.set(17)
}

application {
  mainClass = "duckpond.buriedincode.Badger"
  applicationName = project.name
}

tasks.jar {
  manifest {
    attributes["Main-Class"] = application.mainClass.get()
  }
}

spotless {
  java {
    importOrder()
    removeUnusedImports()
    expandWildcardImports()
    forbidWildcardImports()
    forbidModuleImports()
    cleanthat().sourceCompatibility("17")
    eclipse()
      .sortMembersEnabled(true)
      .sortMembersOrder("SF,F,SI,I,C,SM,M,T")
      .sortMembersVisibilityOrderEnabled(true)
      .sortMembersVisibilityOrder("B,R,D,V")
    princeOfSpace()
      .indentStyle("SPACES")
      .indentSize(2)
      .lineLength(120)
      .wrapStyle("BALANCED")
      .closingParenOnNewLine(true)
      .trailingCommas(true)
      .javaLanguageLevel(17)
    leadingTabsToSpaces(2)
    trimTrailingWhitespace()
  }
  kotlinGradle {
    ktfmt().googleStyle().configure {
      it.setMaxWidth(120)
      it.setBlockIndent(2)
      it.setContinuationIndent(2)
      it.setRemoveUnusedImports(true)
      it.setTrailingCommaManagementStrategy(TrailingCommaManagementStrategy.COMPLETE)
    }
  }
  toml {
    target("gradle/libs.versions.toml")
    versionCatalog().stripQuotedKeys(true)
  }
}

fun isNonStable(version: String): Boolean {
  val stableKeyword = listOf("RELEASE", "FINAL", "GA").any { version.uppercase().contains(it) }
  val regex = "^[0-9,.v-]+(-r)?$".toRegex()
  val isStable = stableKeyword || regex.matches(version)
  return isStable.not()
}

tasks.withType<DependencyUpdatesTask> {
  gradleReleaseChannel = "current"
  checkForGradleUpdate = true
  checkConstraints = false
  checkBuildEnvironmentConstraints = false
  resolutionStrategy {
    componentSelection {
      all(
        Action<ComponentSelectionWithCurrent> {
          if (isNonStable(candidate.version) && !isNonStable(currentVersion)) {
            reject("Release candidate")
          }
        }
      )
    }
  }
}

tasks.register<Exec>("jpackageWindows") {
  dependsOn(tasks.shadowJar)

  val javaHome =
    javaToolchains
      .launcherFor {
        languageVersion = JavaLanguageVersion.of(17)
      }
      .get()
      .metadata
      .installationPath
      .asFile

  val inputDir = layout.buildDirectory.dir("jpackage/input").get().asFile
  val outputDir = layout.buildDirectory.dir("jpackage/output").get().asFile

  doFirst {
    inputDir.mkdirs()
    outputDir.mkdirs()

    copy {
      from(tasks.shadowJar.flatMap { it.archiveFile })
      into(inputDir)
    }
  }

  commandLine(
    javaHome.resolve("bin/jpackage").absolutePath,
    "--type",
    "exe",
    "--name",
    project.name,
    "--app-version",
    project.version,
    "--input",
    inputDir.absolutePath,
    "--main-jar",
    tasks.shadowJar.get().archiveFileName.get(),
    "--main-class",
    application.mainClass.get(),
    "--dest",
    outputDir.absolutePath,
  )
}
