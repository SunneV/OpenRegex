// JavaRegexCLI.java
import com.google.gson.Gson;
import java.util.regex.*;
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.lang.reflect.Field;
import java.util.Map;

public class JavaRegexCLI {
    public static void main(String[] args) {
        if (args.length == 4 && "getFlag".equals(args[0])) {
            String flagName = args[1];
            System.out.println(getFlagValue(flagName));
             System.exit(0);
        }
        if (args.length != 3) {
            System.err.println("Usage: JavaRegexCLI <pattern> <text> <flags>");
            System.exit(1);
        }
        String pattern = args[0];
        String text = args[1];
        int flags = Integer.parseInt(args[2]);

        List<Map<String, Object>> matches = performRegexMatch(pattern, text, flags);

        Gson gson = new Gson();
        Map<String, Object> result = new HashMap<>();
        result.put("matches", matches);
        System.out.println(gson.toJson(result));
    }
    // Method to get a flag value by name
    public static int getFlagValue(String flagName) {
          try {
                Field field = Pattern.class.getField(flagName);
                 return field.getInt(null);
          } catch (NoSuchFieldException | IllegalAccessException e){
            System.err.println("Invalid flag name: " + flagName);
           return 0;
           }

    }
    private static List<Map<String, Object>> performRegexMatch(String pattern, String text, int flags) {
        List<Map<String, Object>> matches = new ArrayList<>();
        try {
            Pattern regexPattern = Pattern.compile(pattern, flags);
            Matcher matcher = regexPattern.matcher(text);
             Map<Integer,String> groupNames=  getGroupNames(regexPattern);

            while (matcher.find()) {
                Map<String, Object> match = new HashMap<>();
                match.put("match", matcher.group(0));
                match.put("index", new int[]{matcher.start(), matcher.end()});

                List<Map<String, Object>> groups = new ArrayList<>();
                for (int i = 1; i <= matcher.groupCount(); i++) {
                    groups.add(getGroupData(matcher, i, groupNames));
                }
                match.put("groups", groups);
                matches.add(match);
            }
        } catch (PatternSyntaxException e) {
             System.err.println("Error during regex match: " + e.getMessage());
        }

        return matches;
    }

    private static Map<Integer, String> getGroupNames(Pattern pattern) {
       Map<Integer, String> groupNames = new HashMap<>();
           try {
            Field namedGroupsField = Pattern.class.getDeclaredField("namedGroups");
             namedGroupsField.setAccessible(true);
              Object namedGroups = namedGroupsField.get(pattern);

                if (namedGroups instanceof Map<?,?>){
                     Map<?,?> namedGroupsMap = (Map<?, ?>) namedGroups;
                    for (Map.Entry<?, ?> entry : namedGroupsMap.entrySet()){
                            if (entry.getKey() instanceof String && entry.getValue() instanceof Integer) {
                                groupNames.put((Integer) entry.getValue(), (String) entry.getKey());
                            }
                   }
                }
               else {
                   Field groupNamesField = Pattern.class.getDeclaredField("groupNames");
                   groupNamesField.setAccessible(true);
                    Object groupNamesObj = groupNamesField.get(pattern);
                    if (groupNamesObj instanceof Map<?,?>) {
                        Map<?,?> groupNamesMap = (Map<?,?>) groupNamesObj;
                          for (Map.Entry<?, ?> entry : groupNamesMap.entrySet()) {
                            if (entry.getKey() instanceof String && entry.getValue() instanceof Integer) {
                                groupNames.put((Integer) entry.getValue(), (String) entry.getKey());
                            }
                        }
                    }

               }


        } catch (NoSuchFieldException| IllegalAccessException e){
            //Ignore, can happen when using older java version
           // System.err.println("Error during get group name: " + e.getMessage());
       }

        return groupNames;
    }
     private static Map<String, Object> getGroupData(Matcher matcher, int groupIndex,  Map<Integer,String> groupNames) {
         Map<String, Object> group = new HashMap<>();
         try {
               if (matcher.group(groupIndex) == null){
                 group.put("name","");
                 group.put("value","");
                 group.put("index", new int[0]);
                 return group;
               }
               group.put("name", groupNames.getOrDefault(groupIndex, ""));
               group.put("value", matcher.group(groupIndex));
               group.put("index", new int[]{matcher.start(groupIndex), matcher.end(groupIndex)});

        }
           catch (Exception e){
                 System.err.println("Error during get group data: " + e.getMessage());
                 group.put("name","");
                 group.put("value","");
                 group.put("index", new int[0]);
           }
        return group;
    }
}