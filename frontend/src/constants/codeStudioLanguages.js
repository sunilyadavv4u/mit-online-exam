/** Code Studio language definitions (Monaco + MIT exam coding languages). */

export const CODE_STUDIO_LANGUAGES = [
  {
    id: 'python',
    label: 'Python',
    monaco: 'python',
    description: 'Python 3 — run in playground',
    canRun: true,
  },
  {
    id: 'sql',
    label: 'SQL Server',
    monaco: 'sql',
    description: 'Run queries (SQLite practice DB, or real SQL Server if configured)',
    canRun: true,
  },
  {
    id: 'pyspark',
    label: 'PySpark',
    monaco: 'python',
    description: 'Run PySpark locally (requires Java + pyspark on server)',
    canRun: true,
  },
  {
    id: 'java',
    label: 'Java',
    monaco: 'java',
    description: 'Compile & run with JDK (javac/java on server)',
    canRun: true,
  },
];

export const CODE_STUDIO_TEMPLATES = {
  python: `# Python 3 — MIT Code Studio
def greet(name):
    return f"Hello, {name}!"

print(greet("MIT"))
`,
  sql: `-- SQL (demo Employee table — TOP/dbo. supported)
SELECT TOP 10 EmployeeID, FirstName, LastName, Department
FROM dbo.Employee
WHERE Department = 'Engineering'
ORDER BY LastName;
`,
  pyspark: `# PySpark — local mode (first run may take 1–2 min)
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("MIT_Code_Studio")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

data = [("Ada", "Engineering"), ("Grace", "Engineering"), ("Alan", "Research")]
df = spark.createDataFrame(data, ["name", "dept"])
df.show()

spark.stop()
`,
  java: `// Java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from MIT Code Studio");
    }
}
`,
};

export function monacoLanguageFor(id) {
  const lang = CODE_STUDIO_LANGUAGES.find((l) => l.id === id);
  return lang?.monaco || 'python';
}
