package com.weblab.service;

import com.weblab.dto.RegisterRequest;
import com.weblab.entity.User;
import com.weblab.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Transactional
    public User register(RegisterRequest request) {
        log.debug("UserService.register() called for user: {}", request.getUsername());

        String username = request.getUsername();
        String email = request.getEmail();

        log.debug("Checking username uniqueness");
        if (userRepository.existsByUsername(username)) {
            log.warn("User '{}' already exists", username);
            throw new IllegalArgumentException("User with this username already exists");
        }

        log.debug("Username is available, creating user");

        User user = new User();
        user.setUsername(username);

        if (email != null && !email.isEmpty()) {
            user.setEmail(email);
        } else {
            user.setEmail(username);
        }

        user.setPassword(passwordEncoder.encode(request.getPassword()));

        log.debug("Saving user to database");
        User savedUser = userRepository.save(user);
        log.info("User '{}' registered successfully", username);

        return savedUser;
    }

    public boolean checkPassword(String inputPassword, String storedPassword) {
        if (storedPassword.startsWith("{noop}")) {
            String plainPassword = storedPassword.substring(6);
            return plainPassword.equals(inputPassword);
        } else if (storedPassword.startsWith("$2a$") || storedPassword.startsWith("$2b$") || storedPassword.startsWith("$2y$")) {
            return passwordEncoder.matches(inputPassword, storedPassword);
        } else {
            return storedPassword.equals(inputPassword);
        }
    }

    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }

    public Optional<User> findById(Long id) {
        return getUserById(id);
    }

    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

}