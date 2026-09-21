# 循环操作注意事项
> 避免内存爆炸 + 双指针优化 | 2026-04-15 | #性能优化 #循环 #内存

## 🎯 核心原则
**不产生新对象是 Android 的生存之道**

## 📝 循环中的内存陷阱

### 问题：循环中创建对象

```java
// ❌ 错误：每次循环都创建新对象
for (int i = 0; i < 10000; i++) {
    Rect rect = new Rect();  // 创建 10000 个对象
    rect.set(i, 0, i+10, 10);
    draw(rect);
}

// ❌ 错误：循环中创建临时集合
val result = mutableListOf<Int>()
for (i in 0 until 10000) {
    val temp = listOf(i, i+1)  // 每次创建新 List
    result.addAll(temp)
}
```
### 解决方案：复用对象

```kotlin
// ✅ 正确：复用同一个对象
Rect rect = new Rect();  // 只创建一次
for (int i = 0; i < 10000; i++) {
    rect.set(i, 0, i+10, 10);
    draw(rect);
}

// ✅ 正确：使用 Array 或复用可变集合
val result = mutableListOf<Int>()
for (i in 0 until 10000) {
    result.add(i)
    result.add(i+1)
}
```

### 危害链
| 后果	| 说明 |
| ---- | ---- |
| 频繁GC	|大量临时对象触发 GC，导致掉帧|
|内存抖动|	内存分配释放频率过高|
|OOM	|对象无法及时回收时直接崩溃|


## 📝 双指针：省时利器
### 典型场景一：两数之和（有序数组）
```kotlin
// 双指针 O(n) vs 嵌套循环 O(n²)
fun twoSum(nums: IntArray, target: Int): IntArray {
    var left = 0
    var right = nums.size - 1
    while (left < right) {
        val sum = nums[left] + nums[right]
        when {
            sum == target -> return intArrayOf(left, right)
            sum < target -> left++
            else -> right--
        }
    }
    return intArrayOf(-1, -1)
}
```

### 典型场景二：快慢指针（链表判环）
```kotlin
fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head
    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
        if (slow == fast) return true
    }
    return false
}
```

### 典型场景三：滑动窗口
```kotlin
fun lengthOfLongestSubstring(s: String): Int {
    var left = 0
    var maxLen = 0
    val charSet = mutableSetOf<Char>()
    
    for (right in s.indices) {
        while (s[right] in charSet) {
            charSet.remove(s[left])
            left++
        }
        charSet.add(s[right])
        maxLen = maxOf(maxLen, right - left + 1)
    }
    return maxLen
}
```

## 🔑 复杂度对比
|方法	|时间复杂度|	空间复杂度|
|--- | --- | --- |
|嵌套循环|O(n²)|O(1)|
|双指针|O(n)|O(1)|
|哈希表|O(n)|O(n)|

## ⚠️ 注意事项
- 循环中尽量复用可变对象（Rect、StringBuilder、ArrayList）
- 优先使用基本类型而非包装类（int 而非 Integer）
- 双指针适用于有序数组、链表、回文判断等场景

**双指针的核心：一快一慢 或 一头一尾**
