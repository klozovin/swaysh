package tinywl

import tinywl.wlroots.util.log_h
import tinywl.wlroots.version_h
import java.lang.foreign.MemorySegment


class TinyWL {
    fun main() {
        println("TinyWL running on Java: ${System.getProperty("java.version")}")
        println("Wlroots (major/minor/micro): " +
                "${version_h.WLR_VERSION_MAJOR()}." +
                "${version_h.WLR_VERSION_MINOR()}." +
                "${version_h.WLR_VERSION_MICRO()}")
        println("Wlroots (str): ${version_h.WLR_VERSION_STR().getUtf8String(0)}")

        // Try some logging
//        val segment = MemorySegment()
//        log_h.wlr_log_init(log_h.WLR_DEBUG(), log_h.NULL())
//        log_h._wlr_log(log_h.WLR_INFO(), )

    }
}
