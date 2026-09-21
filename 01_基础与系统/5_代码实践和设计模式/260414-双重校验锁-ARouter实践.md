
## ARouter 对象创建实践「双重校验锁」
```java
private volatile static boolean hasInit = false;

public static ARouter getInstance() {
    if (!hasInit) {
        throw new InitException("ARouter::Init::Invoke init(context) first!");
    } else {
        if (instance == null) {
            synchronized (ARouter.class) {
                if (instance == null) {
                    instance = new ARouter();
                }
            }
        }
        return instance;
    }
}
```

## 📝 关键点

|  要点  |  说明  |
|  ----  | ---- |
|volatile	| 防止指令重排序，保证多线程下可见性|
|双重检查	| 避免每次获取实例都进入同步块，提升性能|
|构造方法私有	| 防止外部直接 new|

## 总结

> 第一次检查避免每次获取都加锁，第二次检查防止多线程下重复创建实例。  
> `volatile` 禁止指令重排序，避免拿到未完全初始化的对象。
