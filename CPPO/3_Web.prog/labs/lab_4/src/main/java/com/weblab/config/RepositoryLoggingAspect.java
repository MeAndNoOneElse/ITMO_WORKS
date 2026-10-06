package com.weblab.config;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.concurrent.atomic.AtomicInteger;

@Aspect
@Component
@Slf4j
public class RepositoryLoggingAspect {

    private final AtomicInteger queryCounter = new AtomicInteger(0);
    @Around("execution(* com.weblab.repository.*.*(..))")
    public Object logRepositoryCall(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        String repositoryName = joinPoint.getSignature().getDeclaringType().getSimpleName();
        Object[] args = joinPoint.getArgs();

        int queryNumber = queryCounter.incrementAndGet();

        log.info("[DB Query #{}] → {}.{}({})",
                queryNumber,
                repositoryName,
                methodName,
                formatArgs(args));

        long startTime = System.currentTimeMillis();
        Object result = null;
        boolean hasError = false;

        try {
            result = joinPoint.proceed();
            return result;

        } catch (Throwable e) {
            hasError = true;
            log.error("[DB Query #{}] ОШИБКА в {}.{}: {}",
                    queryNumber,
                    repositoryName,
                    methodName,
                    e.getMessage());
            throw e;

        } finally {
            long executionTime = System.currentTimeMillis() - startTime;

            if (!hasError) {
                String resultInfo = formatResult(result);
                log.info("[DB Query #{}] ← {}.{} завершён за {}ms | Результат: {}",
                        queryNumber,
                        repositoryName,
                        methodName,
                        executionTime,
                        resultInfo);
            }
        }
    }

    private String formatArgs(Object[] args) {
        if (args == null || args.length == 0) {
            return "без параметров";
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < args.length; i++) {
            if (i > 0) sb.append(", ");

            Object arg = args[i];
            if (arg == null) {
                sb.append("null");
            } else if (arg.getClass().getName().startsWith("com.weblab.entity")) {
                sb.append(arg.getClass().getSimpleName());
                try {
                    Object id = arg.getClass().getMethod("getId").invoke(arg);
                    sb.append("#").append(id);
                } catch (Exception ignored) {
                    sb.append("(?)");
                }
            } else {
                sb.append(arg.toString());
            }
        }
        return sb.toString();
    }

    private String formatResult(Object result) {
        if (result == null) {
            return "null";
        }

        if (result instanceof java.util.Optional) {
            java.util.Optional<?> opt = (java.util.Optional<?>) result;
            return opt.isPresent() ? "Optional[" + opt.get().getClass().getSimpleName() + "]" : "Optional.empty";
        }

        if (result instanceof java.util.Collection) {
            int size = ((java.util.Collection<?>) result).size();
            return "Collection[size=" + size + "]";
        }

        if (result.getClass().getName().startsWith("com.weblab.entity")) {
            return result.getClass().getSimpleName();
        }

        return result.getClass().getSimpleName();
    }
}

