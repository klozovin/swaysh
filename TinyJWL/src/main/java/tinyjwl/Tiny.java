package tinyjwl;

import jdk.incubator.foreign.CLinker;
import jdk.incubator.foreign.FunctionDescriptor;
import jdk.incubator.foreign.ResourceScope;
import jdk.incubator.foreign.SymbolLookup;
import tinyjwl.wlroots.util.log_h;

import java.lang.invoke.MethodType;
import java.util.List;

public class Tiny {

    public static void main(String[] args) throws Throwable {
        System.out.println("Running Tiny on: " + System.getProperty("java.version"));

        System.loadLibrary("wlroots");
        System.loadLibrary("wayland-server");

        var linker = CLinker.getInstance();
        var sysLookup = CLinker.systemLookup();
        var libLookup = SymbolLookup.loaderLookup();

        // Check whether we can resolve wayland-server/wlroots symbols
        var functions = List.of(
                "wl_display_run",
                "wl_display_create",
                "wl_display_destroy",
                "wl_display_get_event_loop",
                "wlr_seat_get_keyboard",
                "wlr_backend_autocreate",
                "wlr_log_init",
                "wlr_matrix_project_box",
                "wlr_log_importance",
                "wlr_log_get_verbosity"
        );
        for (var fn : functions) {
            var memoryAddress = libLookup.lookup(fn);
            System.out.println(fn + ": " + memoryAddress.isPresent());
        }

        // Scope to allocate strings in
        var scope = ResourceScope.newConfinedScope();

        // Initialize logging and check if it worked
        log_h.wlr_log_init(log_h.WLR_DEBUG(), log_h.NULL());
        System.out.println("Log verbosity should be: " + log_h.WLR_DEBUG());
        System.out.println("Log verbosity is: " + log_h.wlr_log_get_verbosity());

        // Use the previously setup logging to output something
        log_h._wlr_log(log_h.WLR_INFO(), CLinker.toCString("Hello from logging", scope));

        // Show the process PID
        printPid(linker, sysLookup);
    }

    private static void printPid(CLinker linker, SymbolLookup sysLookup) throws Throwable {
        var getpid = linker.downcallHandle(
                sysLookup.lookup("getpid").get(),
                MethodType.methodType(int.class),
                FunctionDescriptor.of(CLinker.C_INT));
        System.out.println("PID: " + (int) getpid.invokeExact());
    }
}