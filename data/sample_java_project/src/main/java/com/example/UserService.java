package com.example;

import java.util.List;
import java.util.ArrayList;

public class UserService {
    public void save(User user) {
        System.out.println(user.getName());
    }

    public User findById(int id) {
        return new User();
    }

    private List<User> findAll() {
        return new ArrayList<>();
    }
}