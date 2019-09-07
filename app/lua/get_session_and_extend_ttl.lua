-- KEYS[1]: token keys
-- ARGS[1]: minial ttl, will be extend if current ttl is smaller

local key = KEYS[1]
local expected_ttl = tonumber(ARGV[1])
local session_value = redis.call("GET", key)
if session_value == nil then
    return nil
else
    -- key exists
    local ttl = redis.call("TTL", key)
    if ttl <= 0 then
        -- key is expired or it's ttl is very short, so set key value
        -- key expired after we get value
        redis.call("SET", key, session_value, 'EX', expected_ttl)
    elseif ttl < expected_ttl then
        -- key is not expired but ttl is not lone enough
        local expired = redis.call("expire", key, expected_ttl)
        if expired == 0 then
            redis.call("SET", key, session_value, 'EX', expected_ttl)
        end
    end

    return session_value
end
