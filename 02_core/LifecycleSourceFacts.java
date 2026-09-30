/* Parse source only; never compile/load/execute the supplied class.
 * Bounded may-write and local-call analysis. Unknown effects fail closed. */
import com.sun.source.tree.*;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import javax.lang.model.element.Modifier;
import javax.tools.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class LifecycleSourceFacts {
    static final class Facts {
        MethodTree method;
        String key;
        Set<String> locals = new HashSet<>();
        Set<String> writes = new TreeSet<>();
        Set<String> calls = new TreeSet<>();
        Set<String> issues = new TreeSet<>();
        Facts(MethodTree m) {
            method=m; key=m.getName()+"/"+m.getParameters().size();
            for (VariableTree p:m.getParameters()) locals.add(p.getName().toString());
        }
    }
    static Map<String,VariableTree> fields=new TreeMap<>();
    static Map<String,List<Facts>> methods=new TreeMap<>();
    static boolean finalClass, atomicImport;

    static ExpressionTree unwrap(ExpressionTree t) {
        while (t instanceof ParenthesizedTree) t=((ParenthesizedTree)t).getExpression();
        return t;
    }
    static String field(ExpressionTree t, Facts f) {
        t=unwrap(t);
        if (t instanceof IdentifierTree) {
            String name=t.toString();
            return fields.containsKey(name) && !f.locals.contains(name) ? name : "";
        }
        if (t instanceof MemberSelectTree) {
            MemberSelectTree s=(MemberSelectTree)t;
            if (s.getExpression().toString().equals("this") && fields.containsKey(s.getIdentifier().toString()))
                return s.getIdentifier().toString();
        }
        return "";
    }
    static boolean atomic(String name) {
        VariableTree v=fields.get(name);
        if (v==null || !v.getModifiers().getFlags().contains(Modifier.FINAL)) return false;
        String type=v.getType().toString();
        return type.equals("java.util.concurrent.atomic.AtomicBoolean") || (atomicImport && type.equals("AtomicBoolean"));
    }
    static void target(ExpressionTree t, Facts f) {
        String name=field(t,f);
        if (!name.isEmpty()) {f.writes.add(name);return;}
        t=unwrap(t);
        if (t instanceof IdentifierTree && f.locals.contains(t.toString())) return;
        f.issues.add("unsupported assignment target: "+t.getKind());
    }
    static String callKey(MethodInvocationTree t) {
        ExpressionTree s=t.getMethodSelect();
        String name;
        if (s instanceof IdentifierTree) name=s.toString();
        else if (s instanceof MemberSelectTree && ((MemberSelectTree)s).getExpression().toString().equals("this"))
            name=((MemberSelectTree)s).getIdentifier().toString();
        else return "";
        return name+"/"+t.getArguments().size();
    }
    static void scanEffects(Facts f) {
        if (f.method.getBody()==null) {f.issues.add("body unavailable");return;}
        for (String local:f.locals) if (fields.containsKey(local)) f.issues.add("parameter shadows field: "+local);
        new TreeScanner<Void,Void>() {
            @Override public Void visitVariable(VariableTree v, Void x) {
                f.locals.add(v.getName().toString());
                if (fields.containsKey(v.getName().toString())) f.issues.add("local shadows field: "+v.getName());
                return super.visitVariable(v,x);
            }
        }.scan(f.method.getBody(),null);
        new TreeScanner<Void,Void>() {
            @Override public Void visitAssignment(AssignmentTree t, Void x) {
                target(t.getVariable(),f);return super.visitAssignment(t,x);
            }
            @Override public Void visitCompoundAssignment(CompoundAssignmentTree t, Void x) {
                target(t.getVariable(),f);return super.visitCompoundAssignment(t,x);
            }
            @Override public Void visitUnary(UnaryTree t, Void x) {
                if (Arrays.asList(Tree.Kind.PREFIX_INCREMENT,Tree.Kind.PREFIX_DECREMENT,
                    Tree.Kind.POSTFIX_INCREMENT,Tree.Kind.POSTFIX_DECREMENT).contains(t.getKind())) target(t.getExpression(),f);
                return super.visitUnary(t,x);
            }
            @Override public Void visitMethodInvocation(MethodInvocationTree t, Void x) {
                String key=callKey(t);
                if (!key.isEmpty()) {
                    List<Facts> matches=methods.getOrDefault(key,Collections.emptyList());
                    if (matches.size()!=1) f.issues.add("unresolved/overloaded call: "+key);
                    else {
                        Set<Modifier> m=matches.get(0).method.getModifiers().getFlags();
                        if (!(finalClass || m.contains(Modifier.PRIVATE) || m.contains(Modifier.FINAL) || m.contains(Modifier.STATIC)))
                            f.issues.add("overridable helper: "+key);
                        else f.calls.add(key);
                    }
                } else if (t.getMethodSelect() instanceof MemberSelectTree) {
                    MemberSelectTree s=(MemberSelectTree)t.getMethodSelect();
                    String receiver=field(s.getExpression(),f);
                    if (s.getIdentifier().contentEquals("set") && t.getArguments().size()==1 && atomic(receiver)) f.writes.add(receiver);
                    else f.issues.add("external/aliased call: "+s.getIdentifier());
                } else f.issues.add("unknown invocation");
                return super.visitMethodInvocation(t,x);
            }
            @Override public Void visitNewClass(NewClassTree t, Void x) {
                f.issues.add("constructor effects outside action grammar");return super.visitNewClass(t,x);
            }
            @Override public Void visitLambdaExpression(LambdaExpressionTree t, Void x) {
                f.issues.add("lambda effects outside action grammar");return null;
            }
            @Override public Void visitMemberReference(MemberReferenceTree t, Void x) {
                f.issues.add("method reference outside action grammar");return null;
            }
            @Override public Void visitEnhancedForLoop(EnhancedForLoopTree t, Void x) {
                f.issues.add("implicit iterator calls outside action grammar");return super.visitEnhancedForLoop(t,x);
            }
            @Override public Void visitTry(TryTree t, Void x) {
                if (!t.getResources().isEmpty()) f.issues.add("implicit resource close outside action grammar");
                return super.visitTry(t,x);
            }
            @Override public Void visitClass(ClassTree t, Void x) {
                f.issues.add("nested class in action");return null;
            }
        }.scan(f.method.getBody(),null);
    }
    static void closure(Facts f, Set<String> path, Set<String> writes, Set<String> issues) {
        writes.addAll(f.writes);issues.addAll(f.issues);
        if (!path.add(f.key)) {issues.add("recursive action call graph: "+f.key);return;}
        for (String key:f.calls) closure(methods.get(key).get(0),path,writes,issues);
        path.remove(f.key);
    }
    static Map<String,Object> describe(Facts f) {
        String returned="";
        final boolean[] hasGuard={false};
        new TreeScanner<Void,Void>() {
            @Override public Void visitMethodInvocation(MethodInvocationTree t, Void x) {
                if (callKey(t).equals("ensureOpen/0")) hasGuard[0]=true;
                return super.visitMethodInvocation(t,x);
            }
        }.scan(f.method.getBody(),null);
        if (f.method.getBody()!=null && f.method.getParameters().isEmpty()) {
            List<? extends StatementTree> ss=f.method.getBody().getStatements();
            int i=0;
            if (ss.size()==2 && ss.get(0) instanceof ExpressionStatementTree) {
                ExpressionTree e=((ExpressionStatementTree)ss.get(0)).getExpression();
                if (e instanceof MethodInvocationTree && callKey((MethodInvocationTree)e).equals("ensureOpen/0")) i=1;
            }
            if (ss.size()==i+1 && ss.get(i) instanceof ReturnTree) {
                ExpressionTree e=((ReturnTree)ss.get(i)).getExpression();
                if (e!=null) returned=field(e,f);
            }
        }
        Set<String> writes=new TreeSet<>(),issues=new TreeSet<>();
        closure(f,new HashSet<>(),writes,issues);
        Map<String,Object> d=new LinkedHashMap<>();
        d.put("name",f.method.getName().toString());d.put("arity",f.method.getParameters().size());
        d.put("public",f.method.getModifiers().getFlags().contains(Modifier.PUBLIC));
        d.put("static",f.method.getModifiers().getFlags().contains(Modifier.STATIC));
        d.put("return_field",returned);d.put("guarded",hasGuard[0]);
        List<String> exceptions=new ArrayList<>();
        for (ExpressionTree e:f.method.getThrows()) {String[] q=e.toString().split("\\.");exceptions.add(q[q.length-1]);}
        Collections.sort(exceptions);d.put("exceptions",exceptions);d.put("writes",writes);d.put("issues",issues);
        return d;
    }
    static String json(Object o) {
        if (o==null) return "null";
        if (o instanceof String) return "\""+((String)o).replace("\\","\\\\").replace("\"","\\\"")
            .replace("\n","\\n").replace("\r","\\r").replace("\t","\\t")+"\"";
        if (o instanceof Boolean || o instanceof Number) return o.toString();
        List<String> entries=new ArrayList<>();
        if (o instanceof Map) {
            for (Map.Entry<?,?> e:((Map<?,?>)o).entrySet()) entries.add(json(e.getKey())+":"+json(e.getValue()));
            return "{"+String.join(",",entries)+"}";
        }
        for (Object v:(Iterable<?>)o) entries.add(json(v));
        return "["+String.join(",",entries)+"]";
    }
    public static void main(String[] args) throws Exception {
        JavaCompiler compiler=ToolProvider.getSystemJavaCompiler();
        if (compiler==null) throw new IllegalStateException("JDK compiler unavailable");
        DiagnosticCollector<JavaFileObject> diagnostics=new DiagnosticCollector<>();
        try (StandardJavaFileManager manager=compiler.getStandardFileManager(diagnostics,null,StandardCharsets.UTF_8)) {
            JavacTask task=(JavacTask)compiler.getTask(null,manager,diagnostics,Arrays.asList("-proc:none"),null,manager.getJavaFileObjects(args[0]));
            CompilationUnitTree unit=task.parse().iterator().next();
            for (Diagnostic<?> d:diagnostics.getDiagnostics()) if (d.getKind()==Diagnostic.Kind.ERROR)
                throw new IllegalArgumentException("Java syntax error at line "+d.getLineNumber());
            ClassTree chosen=null;
            for (Tree t:unit.getTypeDecls()) if (t instanceof ClassTree) {
                ClassTree c=(ClassTree)t;
                if (args[1].equals("*") || c.getSimpleName().contentEquals(args[1])) {
                    if (chosen!=null) throw new IllegalArgumentException("ambiguous class");chosen=c;
                }
            }
            if (chosen==null || chosen.getKind()!=Tree.Kind.CLASS) throw new IllegalArgumentException("named ordinary class unavailable");
            finalClass=chosen.getModifiers().getFlags().contains(Modifier.FINAL);
            for (ImportTree i:unit.getImports()) if (!i.isStatic() && i.getQualifiedIdentifier().toString().equals("java.util.concurrent.atomic.AtomicBoolean")) atomicImport=true;
            new TreeScanner<Void,Void>() {
                @Override public Void visitClass(ClassTree t, Void x) {
                    if (t.getSimpleName().contentEquals("AtomicBoolean")) atomicImport=false;
                    return super.visitClass(t,x);
                }
                @Override public Void visitTypeParameter(TypeParameterTree t, Void x) {
                    if (t.getName().contentEquals("AtomicBoolean")) atomicImport=false;
                    return super.visitTypeParameter(t,x);
                }
            }.scan(unit,null);
            for (Tree t:chosen.getMembers()) {
                if (t instanceof VariableTree) {
                    VariableTree v=(VariableTree)t;
                    if (!v.getModifiers().getFlags().contains(Modifier.STATIC)) fields.put(v.getName().toString(),v);
                }
                if (t instanceof MethodTree && ((MethodTree)t).getReturnType()!=null) {
                    Facts f=new Facts((MethodTree)t);methods.computeIfAbsent(f.key,k->new ArrayList<>()).add(f);
                }
            }
            for (List<Facts> fs:methods.values()) for (Facts f:fs) scanEffects(f);
            List<Map<String,Object>> result=new ArrayList<>();
            for (List<Facts> fs:methods.values()) for (Facts f:fs) {
                if (fs.size()>1) f.issues.add("ambiguous same-arity overload: "+f.key);
                result.add(describe(f));
            }
            Map<String,Object> out=new LinkedHashMap<>();out.put("class_name",chosen.getSimpleName().toString());
            out.put("fields",fields.keySet());out.put("methods",result);System.out.println(json(out));
        }
    }
}
