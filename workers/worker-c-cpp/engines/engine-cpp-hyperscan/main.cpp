#include <iostream>
#include <string>
#include <vector>
#include <hs/hs.h>
#include <nlohmann/json.hpp>

/*
 * OpenRegex Nebula: C++ (Hyperscan) Standalone Subprocess Engine
 * Wraps the Intel Hyperscan library for high-performance block mode scanning.
 */

using json = nlohmann::json;

struct ScanContext {
    json matches;
    std::string text;
    int match_id;
    bool som_enabled;
};

static int match_handler(unsigned int id, unsigned long long from, unsigned long long to, unsigned int flags, void *ctx) {
    ScanContext* context = static_cast<ScanContext*>(ctx);
    json match_item;
    match_item["match_id"] = context->match_id++;

    // If SOM is not enabled, 'from' will be 0 or inaccurate, so we only return the end offset reliably.
    // We approximate start for the UI if SOM is missing, but true support requires SOM.
    unsigned long long start_offset = context->som_enabled ? from : 0; // Or logic to derive it if possible

    match_item["start"] = context->som_enabled ? from : to; // Fallback if no SOM
    match_item["end"] = to;

    if (context->som_enabled) {
        match_item["full_match"] = context->text.substr(from, to - from);
    } else {
        match_item["full_match"] = "Match ends at " + std::to_string(to); // Representation when SOM is off
    }

    match_item["groups"] = json::array(); // Hyperscan does not support sub-capturing groups

    context->matches.push_back(match_item);
    return 0;
}

int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        json req;
        try {
            req = json::parse(line);
        } catch (const json::parse_error& e) {
            std::cout << "{\"success\": false, \"error\": \"Invalid JSON input\"}\n";
            continue;
        }

        std::string pattern_str = req["regex"];
        std::string text = req["text"];
        json flags_array = req["flags"];

        unsigned int hs_flags = 0;
        bool enable_som = false;

        for (const auto& f : flags_array) {
            if (f.is_string()) {
                std::string val = f.get<std::string>();
                if (val == "i") hs_flags |= HS_FLAG_CASELESS;
                if (val == "m") hs_flags |= HS_FLAG_MULTILINE;
                if (val == "s") hs_flags |= HS_FLAG_DOTALL;
                if (val == "u") hs_flags |= HS_FLAG_UTF8 | HS_FLAG_UCP;
                if (val == "e") hs_flags |= HS_FLAG_ALLOWEMPTY;
                if (val == "v") hs_flags |= HS_FLAG_SINGLEMATCH;
                if (val == "b") {
                    hs_flags |= HS_FLAG_SOM_LEFTMOST;
                    enable_som = true;
                }
            }
        }

        // Check incompatible flags based on docs
        if (enable_som && (hs_flags & HS_FLAG_SINGLEMATCH)) {
            json err;
            err["success"] = false;
            err["error"] = "Compilation failed: SOM_LEFTMOST is incompatible with SINGLEMATCH";
            std::cout << err.dump() << std::endl;
            continue;
        }

        hs_database_t *database = nullptr;
        hs_compile_error_t *compile_err = nullptr;

        if (hs_compile(pattern_str.c_str(), hs_flags, HS_MODE_BLOCK, nullptr, &database, &compile_err) != HS_SUCCESS) {
            json err;
            err["success"] = false;
            err["error"] = std::string("Compilation failed: ") + (compile_err ? compile_err->message : "Unknown error");
            std::cout << err.dump() << std::endl;
            hs_free_compile_error(compile_err);
            continue;
        }

        hs_scratch_t *scratch = nullptr;
        if (hs_alloc_scratch(database, &scratch) != HS_SUCCESS) {
            json err;
            err["success"] = false;
            err["error"] = "Failed to allocate scratch space";
            std::cout << err.dump() << std::endl;
            hs_free_database(database);
            continue;
        }

        ScanContext ctx;
        ctx.matches = json::array();
        ctx.text = text;
        ctx.match_id = 0;
        ctx.som_enabled = enable_som;

        if (hs_scan(database, text.c_str(), text.length(), 0, scratch, match_handler, &ctx) != HS_SUCCESS) {
            json err;
            err["success"] = false;
            err["error"] = "Scanning failed";
            std::cout << err.dump() << std::endl;
        } else {
            json response;
            response["success"] = true;
            response["matches"] = ctx.matches;
            std::cout << response.dump() << std::endl;
        }

        hs_free_scratch(scratch);
        hs_free_database(database);
    }
    return 0;
}