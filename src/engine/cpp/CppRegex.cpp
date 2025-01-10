#include <iostream>
#include <regex>
#include <vector>
#include <string>
#include <cstring>

using namespace std;

struct Match {
    char *match;
    size_t start;
    size_t group_count;
    char **groups;
    size_t *group_positions;
};

struct MatchResult {
    Match *matches;
    size_t match_count;
    char *error_message;
};

// Helper function to convert std::string to char*
char *copy_to_char_array(const std::string &str) {
    char *cstr = new char[str.length() + 1];
    strcpy(cstr, str.c_str());
    return cstr;
}

void free_match(Match &match) {
    delete[] match.match;
    for (size_t i = 0; i < match.group_count; ++i) {
        delete[] match.groups[i];
    }
    delete[] match.groups;
    delete[] match.group_positions;
}

// Function to find matches
MatchResult* find_matches_internal(const char *text_cstr, const char *pattern_cstr)
{
    std::string text = text_cstr;
    std::string pattern = pattern_cstr;
    MatchResult *result = new MatchResult();
    result->matches = nullptr;
    result->match_count = 0;
    result->error_message = nullptr;
    try {
       std::regex regex_pattern(pattern);
        std::vector<Match> matches;
        std::sregex_iterator it(text.begin(), text.end(), regex_pattern);
        std::sregex_iterator end;
       while(it != end){
         std::smatch sm = *it;
             Match match;
            match.match = copy_to_char_array(sm.str());
            match.start = sm.position();
             match.group_count = sm.size() - 1;

            if (match.group_count > 0) {
              match.groups = new char*[match.group_count];
              match.group_positions = new size_t[match.group_count];

               for (size_t i = 1; i < sm.size(); ++i) {
                 match.groups[i-1] = copy_to_char_array(sm[i].str());
                 match.group_positions[i-1] = sm.position(i);
              }
            }else{
             match.groups = nullptr;
             match.group_positions = nullptr;
           }
            matches.push_back(match);
            ++it;
        }
     if (!matches.empty()){
      result->match_count = matches.size();
      result->matches = new Match[matches.size()];
      for (size_t i = 0; i < matches.size(); ++i){
        result->matches[i] = matches[i];
      }

    }
    } catch(const std::regex_error & e) {
     result->error_message = copy_to_char_array(e.what());

    }  catch(const std::exception & e) {
     result->error_message = copy_to_char_array(e.what());
  }
  catch(...){
       result->error_message = copy_to_char_array("Unknown error");
  }
    return result;

}

// Function to free memory
extern "C" void free_match_result(MatchResult *result) {
    if (result) {
         if (result->matches){
            for (size_t i = 0; i < result->match_count; ++i) {
             free_match(result->matches[i]);
           }
          delete [] result->matches;
        }
        if (result->error_message) {
            delete[] result->error_message;
        }
        delete result;
    }
}

extern "C" MatchResult *find_matches(const char *text_cstr, const char *pattern_cstr) {
    return find_matches_internal(text_cstr, pattern_cstr);
}